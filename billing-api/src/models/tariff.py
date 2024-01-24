from uuid import uuid4

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from db.postgres import Base


class Tariff(Base):
    __tablename__ = 'tariff'
    __table_args__ = {'extend_existing': True, 'schema': 'content'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(Numeric(6, 2), nullable=False)
    duration = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(DateTime(timezone=True), onupdate=func.now())


class Payment(Base):
    __tablename__ = 'payment'
    __table_args__ = {'schema': 'content'}

    id = mapped_column(Integer, primary_key=True, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    tariff_id = Column(ForeignKey("tariff.id", ondelete="SET NULL"), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(DateTime(timezone=True), onupdate=func.now())
