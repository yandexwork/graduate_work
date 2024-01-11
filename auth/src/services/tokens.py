from datetime import timedelta, datetime
from functools import lru_cache
from uuid import UUID

from fastapi import Response, Request, Depends
from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import Result
from sqlalchemy import select, delete
from redis.asyncio.client import Redis


from src.models.users import User
from src.models.history import LoginHistory
from src.models.tokens import RefreshTokens
from src.schemas.tokens import Tokens, AccessToken
from src.db.postgres import get_session
from src.db.redis_db import get_redis
from src.core.exceptions import WRONG_PASSWORD, REFRESH_TOKEN_IS_INVALID, USER_NOT_FOUND, USER_NOT_AUTHORIZED
from src.core.config import settings, auth_jwt_settings, oauth
from src.services.common import BaseService


class TokenService(BaseService):

    async def get_user_by_login(self, login: str) -> User:
        sql_request = await self.db.execute(select(User).where(User.login == login))
        user: User = sql_request.scalar()
        if not user:
            raise USER_NOT_FOUND
        return user

    async def login(
            self, login: str, password: str, request: Request, response: Response
    ) -> Tokens:
        user = await self.get_user_by_login(login)
        if not user.check_password(password):
            raise WRONG_PASSWORD

        tokens = await self.create_tokens(user.id)
        await self.save_refresh_token(user.id, tokens.refresh_token)
        await self.save_entry_information(user.id, request.headers['user-agent'])
        await self.set_tokens_to_cookie(response, tokens)

        return tokens

    async def refresh(self, user: User, request: Request, response: Response):
        refresh_token_cookie = request.cookies[auth_jwt_settings.authjwt_refresh_cookie_key]

        if await self.is_refresh_token_exist(user.id, refresh_token_cookie):
            access_token = await self.create_access_token(user.id)
            await self.set_access_token_to_cookie(response, access_token.access_token)
            return access_token

        raise REFRESH_TOKEN_IS_INVALID

    async def create_access_token(self, user_id: UUID) -> AccessToken:
        access_token = await self.authorize.create_access_token(
            subject=str(user_id),
            expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        )
        return AccessToken(access_token=access_token)

    async def create_tokens(self, user_id: UUID) -> Tokens:
        access_token = await self.create_access_token(user_id)
        refresh_token = await self.authorize.create_refresh_token(
            subject=str(user_id),
            expires_time=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE)
        )
        return Tokens(
            access_token=access_token.access_token,
            refresh_token=refresh_token
        )

    async def save_refresh_token(self, user_id: UUID, refresh_token: str) -> None:
        refresh_token_entry = RefreshTokens(
            user_id=user_id,
            refresh_token=refresh_token
        )
        await self.update_model_object(refresh_token_entry)

    async def save_entry_information(self, user_id: UUID, user_agent: str) -> None:
        login_history = LoginHistory(
            user_id=user_id,
            user_agent=user_agent
        )
        await self.update_model_object(login_history)

    @staticmethod
    async def set_access_token_to_cookie(response: Response, access_token: str) -> None:
        response.set_cookie('access_token', access_token,
                            settings.ACCESS_TOKEN_EXPIRE,
                            settings.ACCESS_TOKEN_EXPIRE,
                            '/', None, False, True, 'lax')

    async def set_tokens_to_cookie(self, response: Response, tokens: Tokens) -> None:
        await self.set_access_token_to_cookie(response, tokens.access_token)
        response.set_cookie('refresh_token', tokens.refresh_token,
                            settings.REFRESH_TOKEN_EXPIRE,
                            settings.REFRESH_TOKEN_EXPIRE,
                            '/', None, False, True, 'lax')

    async def get_refresh_token_query(self, user_id: UUID, refresh_token: str) -> Result:
        query = await self.db.execute(
            select(RefreshTokens).where(
                RefreshTokens.user_id == user_id
            ).filter(RefreshTokens.refresh_token == refresh_token))
        return query

    async def is_refresh_token_exist(self, user_id: UUID, refresh_token: str) -> bool:
        query = await self.get_refresh_token_query(user_id, refresh_token)
        refresh_token = query.scalar()
        return True if refresh_token else False

    async def delete_refresh_token_by_user_id(self, user_id: UUID):
        await self.db.execute(delete(RefreshTokens).where(RefreshTokens.user_id == user_id))
        await self.db.commit()

    async def logout(self, user_id: UUID) -> None:
        await self.delete_refresh_token_by_user_id(user_id)
        await self.redis.set(
            str(user_id),
            str(datetime.utcnow().timestamp()),
            settings.ACCESS_TOKEN_EXPIRE)
        await self.authorize.unset_jwt_cookies()


@lru_cache()
def get_token_service(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        authorize: AuthJWT = Depends()
) -> TokenService:
    return TokenService(db, redis, authorize)
