import os
import time
import logging
from datetime import datetime, timedelta

from celery import Celery
from yookassa import Payment, Configuration

from models.payment import PaymentModel
from models.subscription import SubscriptionModel, SubscriptionStatus
from models.tariff import TariffModel
from db.postgres import get_sync_session
from core.config import settings


celery = Celery(__name__)
celery.conf.broker_url = settings.celery.broker_url
celery.conf.result_backend = settings.celery.broker_url


@celery.task(name="Check payment status & subscribe")
def subscribe(payment_model_id, payment_id, payment_status):
    Configuration.configure(
        account_id=settings.yookassa_shopid,
        secret_key=settings.yookassa_token
    )
    delay_in_seconds = 30
    tries = 1
    while True:
        time.sleep(delay_in_seconds)
        logging.info(f'Try #{tries}')
        new_payment_data = Payment.find_one(str(payment_id))
        if new_payment_data.status != payment_status:
            session = get_sync_session()
            payment = session.get(PaymentModel, payment_model_id)
            tariff = session.get(TariffModel, payment.tariff_id)
            subscription = SubscriptionModel(
                user_id=payment.user_id,
                tariff_id=payment.tariff_id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=tariff.duration),
                status=repr(SubscriptionStatus.ACTIVE),
                payment_id=payment.id
            )
            payment.status = new_payment_data.status
            session.add(payment)
            session.add(subscription)
            session.commit()
            return (f"Payment {payment.payment_id} changed the status. "
                    f"New subscribe {subscription.id} for user {payment.user_id}.")
        tries += 1
        delay_in_seconds += delay_in_seconds
