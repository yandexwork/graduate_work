from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from services.payment.yookassa_service import YookassaService, get_yookassa_service
from services.jwt_service import get_user_id_from_jwt
from schemas.payment import CreatePaymentSchema, CreatedPaymentSchema


router = APIRouter()


@router.post('/subscribe',
             summary="Подписка",
             response_description="Ссылка на оплату",
             response_model=CreatedPaymentSchema,
             status_code=HTTPStatus.CREATED)
async def subscribe(
        payment_data: CreatePaymentSchema,
        user_id: UUID = Depends(get_user_id_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service)
) -> CreatedPaymentSchema:
    return await payment_service.create_payment(user_id, payment_data.tariff_id)


@router.post('/cancellation',
             summary="Отписка с возвратом",
             status_code=HTTPStatus.OK)
async def unsubscribe(
        user_id: UUID,
        admin_id: UUID = Depends(get_user_id_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
        return_found: bool = False,
) -> int:
    # todo добавить в токен роль чтобы разграничивать поведение
    # if not admin_id.get('is_admin'):
    #     return HTTPStatus.FORBIDDEN
    # else:
    #     return await payment_service.unsubscribe(user_id, return_found)
    return await payment_service.unsubscribe(user_id, return_found)


@router.post('/unsubscribe',
             summary="Отписка",
             status_code=HTTPStatus.OK)
async def unsubscribe(
        user_id: UUID = Depends(get_user_id_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
) -> int:
    return await payment_service.unsubscribe(user_id, False)
