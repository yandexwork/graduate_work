import datetime
from hashlib import md5
from http import HTTPStatus

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Webhook, Payment
from yookassa.domain.exceptions.bad_request_error import BadRequestError
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory

from core.config import settings
from db.postgres import get_async_session
from models.payment import PaymentModel, PaymentStatus
from models.subscription import SubscriptionModel, SubscriptionStatus
from models.tariff import TariffModel
from schemas.tariff import PaymentSchema
from schemas.webhook import YookassaWebhookSchema


class PaymentWebhookError(Exception):
    pass


class YookassaService:

    def __init__(self, session: AsyncSession):
        Configuration.configure(account_id=settings.yookassa_shopid, token=settings.yookassa_token)
        self.session = session
        self.init_webhooks()

    @staticmethod
    def init_webhooks() -> None:
        for webhook_event in [
            WebhookNotificationEventType.PAYMENT_SUCCEEDED,
            WebhookNotificationEventType.PAYMENT_CANCELED,
        ]:
            idempotence_key = md5((webhook_event + settings.webhook_api_url).encode()).hexdigest()
            try:
                Webhook.add(
                    {
                        "event": webhook_event,
                        "url": settings.webhook_api_url,
                    },
                    idempotence_key,
                )
            except BadRequestError as e:
                # logger
                raise PaymentWebhookError

    async def create_payment(self, user_id, tariff_id) -> HTTPStatus | str:
        if self.is_subscribed(user_id):
            return HTTPStatus.NOT_FOUND
        # TODO Сценарий со сменой подписки?
        query = await self.session.execute(select(TariffModel).where(TariffModel.id == tariff_id))
        current_tariff = query.scalars().first()
        if not current_tariff:
            return HTTPStatus.NOT_FOUND

        payment = Payment.create(
            {
                "amount": {
                    "value": float(current_tariff.price),
                    "currency": current_tariff.currency,
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1"
                },
                "capture": True,
                "description": f"Оплата тарифного плана {current_tariff.name}. Стоимость: {current_tariff.price}"
                               f"{current_tariff.currency}.",
                "save_payment_method": True
            }
        )
        new_payment = PaymentModel(
            user_id=user_id,
            tariff_id=current_tariff.id,
            status=payment.status,  # pending
            payment_method_id=payment.payment_method.id,
            payment_id=payment.id
        )
        self.session.add(new_payment)
        await self.session.commit()

        # Пользователь должен перейти по ссылке, а мы ждать вебхука
        return payment.confirmation.confirmation_url

    async def auto_pay(self, user_id):
        if self.is_subscribed(user_id):
            # Если уже подписан и подписка активна
            return HTTPStatus.NOT_FOUND
        query = await self.session.execute(select(SubscriptionModel).where(
            (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == SubscriptionStatus.CANCELED)))
        subscription = query.scalars().first()
        if not subscription:
            return HTTPStatus.NOT_FOUND
        tariff_query = await self.session.execute(select(TariffModel).where(TariffModel.id == subscription.tariff_id))
        tariff = tariff_query.scalars().first()
        payment = Payment.create(
            {
                "amount": {
                    "value": tariff.price,
                    "currency": tariff.currency
                },
                "capture": True,
                "payment_method_id": subscription.payment_method_id,
                "description": tariff.description
            }
        )
        new_payment = PaymentModel(
            user_id=user_id,
            tariff_id=tariff.id,
            status=payment.status,
            payment_method_id=payment.payment_method.id,
            payment_id=payment.id
        )
        self.session.add(new_payment)
        await self.session.commit()

    def unsubscribe(self):
        pass

    async def is_subscribed(self, user_id) -> bool:
        query = await self.session.execute(select(SubscriptionModel).where(
            (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == SubscriptionStatus.ACTIVE)))
        subscription = query.scalars().first()
        if subscription:
            return True
        return False

    async def get_all_payments(self, user_id) -> list[PaymentSchema]:
        query = await self.session.execute(select(PaymentModel).where(PaymentModel.user_id == user_id))
        payments = []
        for payment in query.scalars().all():
            payments.append(
                PaymentSchema(
                    id=payment.id,
                    user_id=payment.user_id,
                    tariff_id=payment.tariff_id
                )
            )
        return payments

    async def recieve_webhook(self, webhook_data: YookassaWebhookSchema) -> HTTPStatus:
        notification_object = WebhookNotificationFactory().create(webhook_data)
        payment = notification_object.object

        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            query = await self.session.execute(select(PaymentModel).where(PaymentModel.payment_id == payment.id))
            payment_db = query.scalars().first()
            if payment_db.status == PaymentStatus.PENDING:
                # создание платежа
                await self.session.execute(update(PaymentModel).where(PaymentModel.payment_id == payment.id).values(
                    status=PaymentStatus.SUCCEEDED))

                # Данные о тарифе
                tariff_query = await self.session.execute(
                    select(TariffModel).where(TariffModel.id == payment_db.tariff_id))
                tariff = tariff_query.scalars().first()

                # Создать запись о подписке
                new_subscription = SubscriptionModel(
                    user_id=payment_db.user_id,
                    tariff_id=payment_db.tariff_id,
                    start_date=datetime.datetime.now(),
                    end_date=datetime.datetime.now() + datetime.timedelta(days=tariff.duration),
                    status=SubscriptionStatus.ACTIVE,
                    payment_method_id=payment_db.payment_method_id
                )
                self.session.add(new_subscription)
                await self.session.commit()
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            query = await self.session.execute(select(PaymentModel).where(PaymentModel.payment_id == payment.id))
            payment_db = query.scalars().first()
            if payment_db.status == PaymentStatus.PENDING:
                await self.session.execute(update(PaymentModel).where(PaymentModel.payment_id == payment.id).values(
                    status=PaymentStatus.CANCELED))
        else:
            # Другое событие
            pass

        return HTTPStatus.OK


def get_yookassa_service(
        session: AsyncSession = Depends(get_async_session)
):
    return YookassaService(session)
