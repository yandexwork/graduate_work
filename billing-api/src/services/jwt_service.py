from uuid import UUID
import json

from fastapi import Depends
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError

from core.exceptions import UserUnauthorizedError
from schemas.user import UserSchema


class JWTService:

    def __init__(self, authorize):
        self.authorize = authorize

    async def get_user_data(self) -> UUID:
        try:
            await self.authorize.jwt_required()
        except (MissingTokenError, JWTDecodeError):
            raise UserUnauthorizedError

        user_data = json.loads(await self.authorize.get_jwt_subject())
        return UserSchema(**user_data)


async def get_user_data_from_jwt(
        authorize: AuthJWT = Depends()
):
    return await JWTService(authorize).get_user_data()
