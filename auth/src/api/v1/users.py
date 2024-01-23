from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Query

from src.models.users import User
from src.services.users import UserService, get_user_service
from src.services.auth import get_user_from_access_token

from src.schemas.users import UserCreateForm, ChangePasswordForm, FullUserSchema
from src.schemas.histories import LoginHistorySchema
from src.schemas.validators import Paginator
from src.core.exceptions import USER_DOES_NOT_HAVE_RIGHTS, MISSING_HEADER_KEY_ERROR, NOT_VALID_HEADER_KEY_ERROR
from src.limiter import limiter
from src.core.config import settings as s


router = APIRouter()


@router.post('/signup')
@limiter.limit("20/minute")
async def create_user(
        request: Request,
        user_create_form: UserCreateForm,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_create_form)


@router.put(
    '/change_password',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def change_password(
        request: Request,
        change_password_form: ChangePasswordForm,
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> None:
    await user_service.change_user_password(user, change_password_form)


def is_valid_key(request: Request, key_name: str, key_value: str) -> bool:
    if key_name in request.headers:
        return request.headers[key_name] == key_value
    raise MISSING_HEADER_KEY_ERROR


@router.put(
    '/subscribe/{user_id}',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def subscribe(
        request: Request,
        user_id: UUID,
        user_service: UserService = Depends(get_user_service)
) -> None:
    if is_valid_key(request, s.subscribe_header_key, s.subscribe_header_value):
        return await user_service.subscribe(user_id)
    raise NOT_VALID_HEADER_KEY_ERROR



@router.put(
    '/unsubscribe/{user_id}',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def unsubscribe(
        request: Request,
        user_id: UUID,
        user_service: UserService = Depends(get_user_service)
) -> None:
    if is_valid_key(request, s.subscribe_header_key, s.subscribe_header_value):
        return await user_service.unsubscribe(user_id)
    raise NOT_VALID_HEADER_KEY_ERROR


@router.get(
    '/get_user_history',
    status_code=HTTPStatus.OK,
    response_model=list[LoginHistorySchema]
)
@limiter.limit("20/minute")
async def get_user_history(
        request: Request,
        paginator: Paginator = Depends(Paginator),
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> list[LoginHistorySchema]:
    return await user_service.get_user_history(user, paginator)


@router.delete('/delete/', status_code=HTTPStatus.NO_CONTENT)
@limiter.limit("20/minute")
async def delete_user(
        request: Request,
        user_id: UUID = Query(),
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> None:
    if user.is_admin():
        return await user_service.delete_user(user_id)
    raise USER_DOES_NOT_HAVE_RIGHTS


@router.get(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=FullUserSchema
)
@limiter.limit("20/minute")
async def get_user_info(
        request: Request,
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> FullUserSchema:
    return await user_service.get_user_info(user)
