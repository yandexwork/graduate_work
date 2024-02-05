import time
import logging
from datetime import datetime, timedelta, date

from celery import Celery
from sqlalchemy import select, cast, Date
from yookassa import Payment, Configuration

from models.payment import PaymentModel, PaymentStatus
from models.subscription import SubscriptionModel, SubscriptionStatus
from models.tariff import TariffModel
from db.postgres import get_sync_session
from core.config import settings
from services.auth_service import auth_subscribe, auth_unsubscribe

celery = Celery(__name__)
celery.conf.broker_url = settings.celery.broker_url
celery.conf.result_backend = settings.celery.broker_url


@celery.task(name="Check payment status & subscribe")
def subscribe(payment_model_id, payment_id, payment_status):
    Configuration.configure(
        account_id=settings.yookassa_shopid,
        secret_key=settings.yookassa_token
    )
    tries = 1
    delay_in_seconds = settings.check_delay_in_seconds
    while True:
        time.sleep(delay_in_seconds)
        logging.info(f'Try #{tries}')
        new_payment_data = Payment.find_one(str(payment_id))
        if new_payment_data.status != payment_status:
            session = get_sync_session()
            payment = session.get(PaymentModel, payment_model_id)
            payment.status = new_payment_data.status
            session.add(payment)
            response_text = f"Payment {payment.payment_id} changed the status. "
            if new_payment_data.status == repr(PaymentStatus.SUCCEEDED):
                tariff = session.get(TariffModel, payment.tariff_id)
                query = session.execute(
                    select(SubscriptionModel).
                    where(SubscriptionModel.user_id == payment.user_id)
                )
                subscription = query.scalars().first()
                # проверяем была ли подписка до этого
                if not subscription:
                    subscription = SubscriptionModel(
                        user_id=payment.user_id,
                        tariff_id=payment.tariff_id,
                        start_date=datetime.now(),
                        end_date=datetime.now() + timedelta(days=tariff.duration),
                        status=repr(SubscriptionStatus.ACTIVE),
                        payment_id=payment.id
                    )
                    session.add(subscription)
                else:
                    subscription.tariff_id = payment.tariff_id
                    subscription.start_date = datetime.now()
                    subscription.end_date = datetime.now() + timedelta(days=tariff.duration)
                    subscription.status = repr(SubscriptionStatus.ACTIVE)
                    subscription.payment_id = payment.id

                response_text += f"New subscribe {subscription.id} for user {payment.user_id}."
            session.commit()
            auth_subscribe(payment.user_id, payment.tariff_id)
            return response_text
        tries += 1
        delay_in_seconds += delay_in_seconds


@celery.task(name="Auto pay or subscribe cancellation")
def auto_pay():
    Configuration.configure(
        account_id=settings.yookassa_shopid,
        secret_key=settings.yookassa_token
    )
    while True:
        logging.info("Run checking subscriptions")
        session = get_sync_session()
        subscriptions = session.query(SubscriptionModel).filter(cast(SubscriptionModel.end_date, Date) == date.today(), SubscriptionModel.status == str(SubscriptionStatus.ACTIVE)).all()
        for subscription in subscriptions:
            tariff = session.get(TariffModel, subscription.tariff_id)
            old_payment_db = session.get(PaymentModel, subscription.payment_id)
            payment = Payment.create(
                {
                    "amount": {
                        "value": tariff.price,
                        "currency": tariff.currency
                    },
                    "capture": True,
                    "payment_method_id": old_payment_db.payment_method_id,
                    "description": tariff.description
                }
            )
            new_payment = PaymentModel(
                user_id=subscription.user_id,
                tariff_id=tariff.id,
                status=payment.status,
                payment_method_id=payment.payment_method.id,
                payment_id=payment.id
            )
            session.add(new_payment)
            session.commit()

            subscription.payment_id = new_payment.id
            if payment.status == 'succeeded':
                subscription.end_date = datetime.now() + timedelta(days=tariff.duration)
            else:
                subscription.status = str(SubscriptionStatus.CANCELED)
                auth_unsubscribe(subscription.user_id)
            session.commit()
        time.sleep(settings.auto_pay_delay)
