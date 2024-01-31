from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.mixins import UUIDMixin, TimeStampedMixin


class RefundModel(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "refund"

    payment_id = Column(String, nullable=False)
    refund_id = Column(UUID, nullable=False)
    amount = Column(Numeric(6, 2), nullable=False)
    status = Column(String, nullable=False)
