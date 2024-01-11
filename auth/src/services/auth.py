from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError
from authlib.integrations.base_client.errors import MismatchingStateError
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request as StarletteRequest
from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import OAUTH_ERROR
from src.core.exceptions import USER_NOT_AUTHORIZED, USER_NOT_FOUND, ACCESS_TOKEN_IS_INVALID, REFRESH_TOKEN_IS_INVALID
from src.db.postgres import get_session
from src.db.redis_db import get_redis
from src.models.users import User
from src.services.common import BaseService


class AuthService(BaseService):

    async def get_user_id_from_token(self, token_required_func) -> UUID:
        try:
            await token_required_func()
        except (MissingTokenError, JWTDecodeError):
            raise USER_NOT_AUTHORIZED

        user_id = await self.authorize.get_jwt_subject()
        if not user_id:
            raise USER_NOT_FOUND
        return user_id

    async def is_token_created_before_logout(self, user: User) -> bool:
        logout_time = await self.redis.get(str(user.id))
        if logout_time:
            token = await self.authorize.get_raw_jwt()
            created_at = token['iat']
            if created_at <= float(logout_time.decode()):
                return True
        return False

    async def get_user_from_token(self, token_required_func, token_exception) -> User:
        user_id = await self.get_user_id_from_token(token_required_func)
        user: User = await self.get_user_by_id(user_id)

        if await self.is_token_created_before_logout(user):
            await self.authorize.unset_jwt_cookies()
            raise token_exception

        return user

    async def get_user_from_access(self):
        token_required_func = self.authorize.jwt_required
        token_exception = ACCESS_TOKEN_IS_INVALID
        return await self.get_user_from_token(
            token_required_func, token_exception
        )

    async def get_user_from_refresh(self):
        token_required_func = self.authorize.jwt_refresh_token_required
        token_exception = REFRESH_TOKEN_IS_INVALID
        return await self.get_user_from_token(
            token_required_func, token_exception
        )


async def get_user_from_access_token(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        authorize: AuthJWT = Depends()
) -> User:
    return await AuthService(db, redis, authorize).get_user_from_access()


async def get_user_from_refresh_token(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        authorize: AuthJWT = Depends()
) -> User:
    return await AuthService(db, redis, authorize).get_user_from_refresh()


async def get_user_info_from_request(
        request: StarletteRequest,
        oauth_service: OAuth
) -> dict:
    try:
        token = await oauth_service.authorize_access_token(request)
    except MismatchingStateError:
        raise OAUTH_ERROR
    user_info = token['userinfo']
    return user_info
