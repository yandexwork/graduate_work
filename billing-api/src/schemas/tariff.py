from uuid import UUID

from pydantic import BaseModel


class TariffSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: int


class PaymentSchema(BaseModel):
    id: int
    user_id: UUID
    tariff_id: UUID

class PaymentResponseSchema:
    id: str
    status: str
    auto_pay_id: str
    last_card_digits: int
