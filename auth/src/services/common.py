from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis

from src.core.exceptions import USER_NOT_FOUND
from src.models.users import User


class BaseService:

    def __init__(
            self, db: AsyncSession,
            redis: Redis = None,
            authorize: AuthJWT = None):
        self.db = db
        self.redis = redis
        self.authorize = authorize

    async def update_model_object(self, model_object) -> None:
        self.db.add(model_object)
        await self.db.commit()
        await self.db.refresh(model_object)

    async def get_user_by_id(self, user_id: UUID) -> User:
        user: User = await self.db.get(User, user_id)
        if not user:
            raise USER_NOT_FOUND
        return user

