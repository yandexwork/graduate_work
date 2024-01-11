from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import Result
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError

from src.db.postgres import get_session
from src.core.exceptions import ROLE_NOT_FOUND, USER_DOES_NOT_HAVE_ROLE, ROLE_ALREADY_EXIST
from src.models.roles import Role
from src.models.users import User
from src.schemas.roles import RoleCreateForm, RoleAttachForm, RoleUpdateForm
from src.schemas.validators import Paginator
from src.services.common import BaseService


class RolesService(BaseService):

    async def get_roles(self, paginator: Paginator) -> list[Role]:
        query = await self.get_roles_query(paginator.page_number, paginator.page_size)
        roles = await self.get_roles_from_query(query)
        return roles

    async def get_user_roles(self, user_id: UUID) -> list[Role]:
        user = await self.db.get(User, user_id)
        return user.roles

    @staticmethod
    async def get_roles_from_query(query: Result) -> list[Role]:
        roles = [role for role in query.scalars().all()]
        return roles

    async def get_roles_query(self, page_number: int, page_size: int) -> Result:
        query = await self.db.execute(
            select(Role)
            .offset((page_number - 1) * page_size)
            .limit(page_size)
        )
        return query

    async def create_role(self, role_create_form: RoleCreateForm) -> Role:
        role = Role(name=role_create_form.name)
        try:
            await self.update_model_object(role)
        except IntegrityError:
            raise ROLE_ALREADY_EXIST
        return role

    async def attach_role(self, role_attach_form: RoleAttachForm) -> None:
        user = await self.get_user_by_id(role_attach_form.user_id)
        role = await self.get_role_by_id(role_attach_form.role_id)
        user.roles.append(role)
        await self.db.commit()

    async def detach_role(self, role_attach_form: RoleAttachForm) -> None:
        user = await self.get_user_by_id(role_attach_form.user_id)
        role = await self.get_role_by_id(role_attach_form.role_id)
        self.remove_role_from_user(user, role)
        await self.db.commit()

    @staticmethod
    def remove_role_from_user(user: User, role: Role) -> None:
        try:
            user.roles.remove(role)
        except ValueError:
            raise USER_DOES_NOT_HAVE_ROLE

    async def delete_role(self, role_id: UUID):
        role = await self.get_role_by_id(role_id)
        await self.db.delete(role)
        await self.db.commit()

    async def update_role(self, role_id: UUID, role_update_form: RoleUpdateForm) -> Role:
        role = await self.get_role_by_id(role_id)
        await self.update_role_data(role, role_update_form)
        return role

    async def get_role_by_id(self, role_id: UUID) -> Role:
        role: Role = await self.db.get(Role, role_id)
        if not role:
            raise ROLE_NOT_FOUND
        return role

    async def update_role_data(self, role: Role, role_update_form: RoleUpdateForm) -> None:
        # DTO - data transfer object
        role_dto = jsonable_encoder(role_update_form)
        for key, value in role_dto.items():
            setattr(role, key, value)
        await self.update_model_object(role)


@lru_cache()
def get_role_service(
        db: AsyncSession = Depends(get_session)
) -> RolesService:
    return RolesService(db)
