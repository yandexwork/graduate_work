from uuid import UUID

from fastapi import Depends
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError

from core.exceptions import UserUnauthorizedError


class JWTService:

    def __init__(self, authorize):
        self.authorize = authorize

    async def get_user_id_from_access_token(self) -> UUID:
        try:
            await self.authorize.jwt_required()
        except (MissingTokenError, JWTDecodeError):
            raise UserUnauthorizedError

        user_id = await self.authorize.get_jwt_subject()
        return user_id


async def get_user_id_from_jwt(
        authorize: AuthJWT = Depends()
):
    return await JWTService(authorize).get_user_id_from_access_token()