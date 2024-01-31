from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment, Refund
from yookassa.refund import RefundResponse

from core.config import settings
from core.exceptions import AlreadySubscribedError, TariffNotFoundError, RefundError, SubscriptionNotFoundError
from db.postgres import get_async_session
from models.payment import PaymentModel, PaymentStatus
from models.subscription import SubscriptionModel, SubscriptionStatus
from models.refund import RefundModel
from models.tariff import TariffModel
from schemas.tariff import PaymentSchema, SubscriptionSchema
from schemas.payment import CreatedPaymentSchema
from tasks import subscribe


class PaymentWebhookError(Exception):
    pass


class YookassaService:

    SUCCEEDED = 'succeeded'

    def __init__(self, session: AsyncSession):
        Configuration.configure(
            account_id=settings.yookassa_shopid,
            secret_key=settings.yookassa_token
        )
        self.session = session

    async def create_payment(self, user_id: UUID, tariff_id: UUID) -> str:

        if await self.is_subscribed(user_id):
            raise AlreadySubscribedError

        tariff = await self.session.get(TariffModel, tariff_id)
        if not tariff:
            raise TariffNotFoundError

        payment_payload = self.create_payment_payload(tariff)
        payment = Payment.create(payment_payload)
        payment_db = await self.save_payment(user_id, tariff, payment)
        subscribe.delay(payment_db.id, payment.id, payment.status)

        return CreatedPaymentSchema(redirect_url=payment.confirmation.confirmation_url)

    @staticmethod
    def create_payment_payload(tariff: TariffModel) -> dict:
        return {
            "amount": {
                "value": float(tariff.price),
                "currency": tariff.currency,
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.payment_redirect_url
            },
            "capture": True,
            "description": f"Оплата тарифного плана {tariff.name}. Стоимость: {tariff.price}"
                           f"{tariff.currency}.",
            "save_payment_method": True
        }

    async def save_payment(self, user_id: UUID, tariff: TariffModel, payment: Payment) -> PaymentModel:
        new_payment = PaymentModel(
            user_id=user_id,
            tariff_id=tariff.id,
            status=payment.status,
            payment_method_id=payment.payment_method.id,
            payment_id=payment.id
        )
        self.session.add(new_payment)
        await self.session.commit()
        return new_payment

    async def unsubscribe(self, user_id: UUID, return_funds: bool) -> None:
        subscription = await self.get_user_subscription(user_id)

        if return_funds:
            tariff = await self.session.get(TariffModel, subscription.tariff_id)
            payment_db = await self.session.get(PaymentModel, subscription.payment_id)
            payload = self.get_refund_payload(payment_db.payment_id, tariff.price, tariff.currency)

            refund = Refund.create(payload)
            await self.save_refund(refund)

            if refund.status != self.SUCCEEDED:
                raise RefundError

        subscription.status = str(SubscriptionStatus.CANCELED)
        self.session.add(subscription)
        await self.session.commit()

    async def save_refund(self, refund: RefundResponse) -> None:
        refund_db = RefundModel(
            payment_id=refund.payment_id,
            refund_id=refund.id,
            status=refund.status,
            amount=refund.amount.value
        )
        self.session.add(refund_db)
        await self.session.commit()

    @staticmethod
    def get_refund_payload(payment_id: UUID, amount: float, currency: str) -> dict:
        payload = {
            "payment_id": str(payment_id),
            "amount": {
                "value": str(amount),
                "currency": currency
            }
        }
        return payload

    async def get_user_subscription(self, user_id: UUID) -> SubscriptionModel:
        subscription_query = await self.session.execute(
            select(SubscriptionModel).
            where(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.status == str(SubscriptionStatus.ACTIVE)
            )
        )
        subscription = subscription_query.scalars().first()
        if subscription:
            return subscription

        raise SubscriptionNotFoundError

    async def is_subscribed(self, user_id) -> bool:
        query = await self.session.execute(select(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id, SubscriptionModel.status == str(SubscriptionStatus.ACTIVE)
        ))
        subscription = query.scalars().first()
        if subscription:
            return True
        return False

    async def get_all_payments(self, user_id) -> list[PaymentSchema]:
        query = await self.session.execute(select(PaymentModel).where(
            PaymentModel.user_id == user_id
        ))
        payments = []
        for payment in query.scalars().all():
            payments.append(
                PaymentSchema(
                    id=payment.id,
                    user_id=payment.user_id,
                    tariff_id=payment.tariff_id,
                    status=payment.status
                )
            )
        return payments

    async def get_all_subscriptions(self, user_id) -> list[SubscriptionSchema]:
        query = await self.session.execute(select(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id, SubscriptionModel.status == str(SubscriptionStatus.ACTIVE)))
        subscriptions = []
        for subscription in query.scalars().all():
            subscriptions.append(
                SubscriptionSchema(
                    id=subscription.id,
                    user_id=subscription.user_id,
                    tariff_id=subscription.tariff_id,
                    start_date=subscription.start_date,
                    end_date=subscription.end_date,
                    status=subscription.status,
                    payment_id=subscription.payment_id
                )
            )
        return subscriptions


def get_yookassa_service(
        session: AsyncSession = Depends(get_async_session)
):
    return YookassaService(session)
