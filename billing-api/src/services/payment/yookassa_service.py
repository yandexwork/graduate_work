import datetime
from hashlib import md5
from http import HTTPStatus
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Webhook, Payment, Refund
from yookassa.domain.exceptions.bad_request_error import BadRequestError
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory

from core.config import settings
from core.exceptions import AlreadySubscribedError, TariffNotFoundError
from db.postgres import get_async_session
from models.payment import PaymentModel, PaymentStatus
from models.subscription import SubscriptionModel, SubscriptionStatus
from models.tariff import TariffModel
from schemas.tariff import PaymentSchema, SubscriptionSchema
from schemas.webhook import YookassaWebhookSchema
from schemas.payment import CreatedPaymentSchema
from tasks import subscribe


class PaymentWebhookError(Exception):
    pass


class YookassaService:

    def __init__(self, session: AsyncSession):
        Configuration.configure(
            account_id=settings.yookassa_shopid,
            secret_key=settings.yookassa_token
        )
        self.session = session
        # self.init_webhooks()

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

    async def auto_pay(self, user_id):
        query = await self.session.execute(select(SubscriptionModel).where(
            (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == SubscriptionStatus.ACTIVE)))
        subscription = query.scalars().first()
        if not subscription:
            return HTTPStatus.NOT_FOUND
        tariff_query = await self.session.execute(select(TariffModel).where(TariffModel.id == subscription.tariff_id))
        tariff = tariff_query.scalars().first()

        old_payment_query = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.payment_id == subscription.payment_id)
        )
        old_payment = old_payment_query.scalars().first()


        # Отправляем платеж в Yookassa
        payment = Payment.create(
            {
                "amount": {
                    "value": tariff.price,
                    "currency": tariff.currency
                },
                "capture": True,
                "payment_method_id": old_payment.payment_id,
                "description": tariff.description
            }
        )

        # Добавляем payment в БД
        new_payment = PaymentModel(
            user_id=user_id,
            tariff_id=tariff.id,
            status=payment.status,
            payment_method_id=payment.payment_method.id,
            payment_id=payment.id
        )
        self.session.add(new_payment)
        await self.session.commit()


        # Получаем новый платеж из БД
        current_payment_query = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.payment_id == payment.id)
        )
        current_payment = current_payment_query.scalars().first()

        # Обновляем в подписке поля для возможного возврата денег
        await self.session.execute(
            update(SubscriptionModel)
            .where((SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == str(SubscriptionStatus.CANCELED)))
            .values(
                status=SubscriptionStatus.ACTIVE,
                payment_id=current_payment.payment_id
            )
        )

    async def unsubscribe(self, user_id, return_founds):
        is_subscribed = await self.is_subscribed(user_id)
        if not is_subscribed:
            # Если не подписан
            return HTTPStatus.NOT_FOUND

        # Получаем данные о подписке
        subscription_query = await self.session.execute(
            select(SubscriptionModel).
            where((SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == str(SubscriptionStatus.ACTIVE)))
        )
        subscription = subscription_query.scalars().first()
        # Надо ли возвращать деньги?
        delta = (datetime.datetime.now() - subscription.end_date).days
        if delta and return_founds:
            # Получить данные о тарифе для просчета стоимость возврата
            tariff_query = await self.session.execute(
                select(TariffModel)
                .where(TariffModel.id == subscription.tariff_id)
            )
            tariff = tariff_query.scalars().first()
            refund_amount = tariff.price / tariff.duration * delta
            res = Refund.create({
                "payment_id": subscription.payment_id,
                "description": "Возврат оставшихся средств по подписке",
                "amount": {
                    "value": refund_amount,
                    "currency": tariff.currency
                }
            })
            if res.status == 'succeeded':
                return HTTPStatus.OK
            else:
                return HTTPStatus.BAD_REQUEST

        try:
            await self.session.execute(
                update(
                    SubscriptionModel
                ).where(
                    (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == str(SubscriptionStatus.ACTIVE))
                ).values(
                    status=SubscriptionStatus.CANCELED)
            )
            return HTTPStatus.OK
        except IOError:
            return HTTPStatus.EXPECTATION_FAILED

    async def is_subscribed(self, user_id) -> bool:
        query = await self.session.execute(select(SubscriptionModel).where(
            (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == str(SubscriptionStatus.ACTIVE))))
        subscription = query.scalars().first()
        if subscription:
            return True
        return False

    async def get_all_payments(self, user_id) -> list[PaymentSchema]:
        query = await self.session.execute(select(PaymentModel).where((
            PaymentModel.user_id == UUID(user_id)) & (PaymentModel.status == str(PaymentStatus.SUCCEEDED))))
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
            (SubscriptionModel.user_id == user_id) & (SubscriptionModel.status == str(SubscriptionStatus.ACTIVE))))
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

    async def recieve_webhook(self, webhook_data: YookassaWebhookSchema) -> HTTPStatus:
        notification_object = WebhookNotificationFactory().create(webhook_data)
        payment = notification_object.object

        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            query = await self.session.execute(select(PaymentModel).where(PaymentModel.payment_id == payment.id))
            payment_db = query.scalars().first()

            if payment_db.status == PaymentStatus.PENDING:
                # создание платежа
                await self.session.execute(
                    update(PaymentModel)
                    .where(PaymentModel.payment_id == payment.id)
                    .values(status=PaymentStatus.SUCCEEDED)
                )

                # Данные о тарифе
                tariff_query = await self.session.execute(
                    select(TariffModel)
                    .where(TariffModel.id == payment_db.tariff_id)
                )
                tariff = tariff_query.scalars().first()

                # Создать запись о подписке
                new_subscription = SubscriptionModel(
                    user_id=payment_db.user_id,
                    tariff_id=payment_db.tariff_id,
                    start_date=datetime.datetime.now(),
                    end_date=datetime.datetime.now() + datetime.timedelta(days=tariff.duration),
                    status=SubscriptionStatus.ACTIVE,
                    payment_id=payment_db.payment_id
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
