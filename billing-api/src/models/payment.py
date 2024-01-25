from enum import Enum

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.mixins import TimeStampedMixin, UUIDMixin
from models.tariff import TariffModel


class PaymentStatus(Enum):
    SUCCEEDED = 'succeeded'
    PENDING = 'pending'
    CANCELED = 'canceled'

    def __repr__(self):
        return self.value

class PaymentModel(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = 'payment'

    user_id = Column(UUID, nullable=False)
    tariff_id = Column(ForeignKey(TariffModel.id, ondelete="SET NULL"), nullable=False)
    status = Column(String)
    payment_method_id = Column(UUID, nullable=False)
    payment_id = Column(UUID, nullable=False)
