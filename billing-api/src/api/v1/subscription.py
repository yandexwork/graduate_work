from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, Response

from schemas.tariff import PaymentSchema, SubscriptionSchema
from services.payment.yookassa_service import YookassaService, get_yookassa_service
from services.jwt_service import get_user_data_from_jwt
from schemas.payment import CreatePaymentSchema, CreatedPaymentSchema, PaymentHistorySchema
from schemas.user import UserSchema
from core.exceptions import UserDoesntHaveRightsError


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


@router.post('/cancellation',
             summary="Отписка с возвратом",
             status_code=HTTPStatus.OK)
async def cancellation(
        user_id: UUID,
        admin_data: UserSchema = Depends(get_user_data_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
        return_fund: bool = False,
) -> Response:
    if 'admin' in admin_data.roles:
        await payment_service.unsubscribe(user_id, return_fund)
        return Response(content='success')
    raise UserDoesntHaveRightsError



@router.post('/unsubscribe',
             summary="Отписка",
             status_code=HTTPStatus.OK)
async def unsubscribe(
        user_data: UserSchema = Depends(get_user_data_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
) -> Response:
    return_fund = False
    await payment_service.unsubscribe(user_data.user_id, return_fund)
    return Response(content='success')



@router.get('/history',
            summary="История платежей",
            response_model=list[PaymentSchema],
            status_code=HTTPStatus.OK)
async def history(
        user_data: UUID = Depends(get_user_data_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
) -> list[PaymentSchema]:
    return await payment_service.get_all_payments(user_data.user_id)


@router.get('/subscriptions',
            summary="Активные подписки",
            response_model=list[SubscriptionSchema],
            status_code=HTTPStatus.OK)
async def history(
        user_data: UserSchema = Depends(get_user_data_from_jwt),
        payment_service: YookassaService = Depends(get_yookassa_service),
) -> list[SubscriptionSchema]:
    return await payment_service.get_all_subscriptions(user_data.user_id)
