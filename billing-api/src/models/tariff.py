from sqlalchemy import Column, String, Text, Integer, Boolean, Numeric

from db.postgres import Base
from models.mixins import TimeStampedMixin, UUIDMixin


class TariffModel(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = 'tariff'

    name = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(Numeric(6, 2), nullable=False)
    currency = Column(String(3))
    duration = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
