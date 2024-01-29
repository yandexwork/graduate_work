from http import HTTPStatus

from fastapi import APIRouter, Depends

from services.payment.yookassa_service import YookassaService, get_yookassa_service
from services.jwt_service import get_user_data_from_jwt
from schemas.payment import CreatePaymentSchema, CreatedPaymentSchema
from schemas.user import UserSchema


router = APIRouter()


@router.post('/subscribe',
             summary="Подписка",
             response_description="Ссылка на оплату",
             response_model=CreatedPaymentSchema,
             status_code=HTTPStatus.CREATED)
async def subscribe(
        payment_data: CreatePaymentSchema,
        user_data: UserSchema = Depends(get_user_data_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service)
) -> CreatedPaymentSchema:
    return await payment_service.create_payment(user_data.user_id, payment_data.tariff_id)
