from db.postgres import Base
from models.mixins import UUIDMixin, TimeStampedMixin
from sqlalchemy import Column, String, Integer


class RefundModel(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "refund"

    payment_id = Column(String)
    amount = Column(Integer)
    status = Column(String)
