from http import HTTPStatus
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, validator

from src.core.exceptions import CustomException, ErrorMessagesUtil


class UserCreateForm(BaseModel):
    login: str = 'testuser'
    password: str = 'qwerty12345'
    first_name: str = 'bob'
    last_name: str = 'smith'

    @validator('password')
    def validate_password(cls, pswd):
        if len(pswd) < 8:
            raise CustomException(
                status_code=HTTPStatus.BAD_REQUEST,
                message=ErrorMessagesUtil.password_is_weak()
            )
        return pswd


class UserLoginForm(BaseModel):
    login: str = "testuser"
    password: str = "qwerty12345"


class ChangePasswordForm(BaseModel):
    previous_password: str = 'qwerty12345'
    new_password: str = 'qwerty123456'


class FullUserSchema(BaseModel):
    id: UUID
    login: str
    password: str
    first_name: str
    last_name: str
    created_at: datetime
    is_admin: bool

