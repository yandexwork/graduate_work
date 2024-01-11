from uuid import UUID

from pydantic import BaseModel


class RoleBaseModel(BaseModel):
    name: str


class RoleCreateForm(RoleBaseModel):
    pass


class RoleSchema(RoleBaseModel):
    id: UUID


class RoleUpdateForm(RoleBaseModel):
    pass


class RoleAttachForm(BaseModel):
    user_id: UUID
    role_id: UUID
