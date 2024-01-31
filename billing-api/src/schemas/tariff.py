import datetime
from uuid import UUID

from pydantic import BaseModel


class TariffSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: int


class PaymentSchema(BaseModel):
    id: UUID
    user_id: UUID
    tariff_id: UUID
    status: str


class PaymentResponseSchema:
    id: UUID
    status: str
    auto_pay_id: str
    last_card_digits: int


class SubscriptionSchema(BaseModel):
    id: UUID
    user_id: UUID
    tariff_id: UUID
    start_date: datetime.datetime
    end_date: datetime.datetime
    status: str
    payment_id: UUID
