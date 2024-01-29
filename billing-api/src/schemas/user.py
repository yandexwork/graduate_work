from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: str
    roles: list[str]
    subscription: str
