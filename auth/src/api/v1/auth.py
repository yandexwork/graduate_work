from http import HTTPStatus

from fastapi import APIRouter, Response, Request, Depends
from starlette.requests import Request as StarletteRequest

from src.models.users import User
from src.schemas.tokens import Tokens, AccessToken
from src.schemas.users import UserLoginForm

from src.services.auth import get_user_from_access_token, get_user_from_refresh_token
from src.services.tokens import TokenService, get_token_service
from src.services.users import UserService, get_user_service
from src.services.auth import get_user_info_from_request
from src.core.config import oauth_services
from src.limiter import limiter


router = APIRouter()


@router.post('/login',
             response_model=Tokens,
             status_code=HTTPStatus.OK)
@limiter.limit("20/minute")
async def get_tokens(
        payload: UserLoginForm,
        response: Response,
        request: Request,
        token_service: TokenService = Depends(get_token_service)
) -> Tokens:
    """Вход пользователя в систему"""
    return await token_service.login(payload.login, payload.password,
                                     request, response)


@router.get("/oauth/{service}",
            response_model=Tokens,
            status_code=HTTPStatus.OK)
@limiter.limit("20/minute")
async def auth_via_service(
        service: str,
        request: StarletteRequest,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service)
):
    if service in oauth_services:
        oauth_service = oauth_services[service]
        user_info = await get_user_info_from_request(request, oauth_service)
        user = await user_service.get_or_create_user(user_info)
        tokens = await token_service.create_tokens(user.id)
        return tokens


@router.get("/login/google")
@limiter.limit("20/minute")
async def login_via_google(request: StarletteRequest):
    redirect_uri = request.url_for('auth_via_service', service='google')
    return await oauth_services['google'].authorize_redirect(request, redirect_uri)


@router.post(
    '/refresh',
    response_model=AccessToken,
    status_code=HTTPStatus.OK
)
@limiter.limit("20/minute")
async def refresh_access_token(
        response: Response,
        request: Request,
        user: User = Depends(get_user_from_refresh_token),
        token_service: TokenService = Depends(get_token_service)
) -> AccessToken:
    """Обновление access токена"""
    return await token_service.refresh(user, request, response)


@router.get(
    '/logout',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def logout_from_all_devices(
        request: Request,
        user: User = Depends(get_user_from_access_token),
        token_service: TokenService = Depends(get_token_service)
) -> None:
    """Выход из аккаунта со всех устройств"""
    await token_service.logout(user.id)

