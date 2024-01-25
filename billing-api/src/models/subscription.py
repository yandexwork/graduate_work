from enum import Enum

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.mixins import TimeStampedMixin, UUIDMixin
from models.payment import PaymentModel
from models.tariff import TariffModel


class SubscriptionStatus(Enum):
    ACTIVE = 'active'
    CANCELED = 'canceled'

    def __repr__(self):
        return self.value

class SubscriptionModel(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "subscription"

    user_id = Column(UUID, nullable=False)
    tariff_id = Column(UUID, ForeignKey(TariffModel.id))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)
    payment_id = Column(UUID, ForeignKey(PaymentModel.id))
