from typing import Any
from http import HTTPStatus


class BaseError(Exception):
    ...


class BaseErrorWithContent(BaseError):
    status_code: int
    content: dict[str, Any]


class AlreadySubscribedError(BaseErrorWithContent):
    status_code = HTTPStatus.CONFLICT
    content = {'message': 'User is already subscribed'}


class TariffNotFoundError(BaseErrorWithContent):
    status_code = HTTPStatus.NOT_FOUND
    content = {'message': 'Tariff is not found'}


class UserUnauthorizedError(BaseErrorWithContent):
    status_code = HTTPStatus.UNAUTHORIZED
    content = {'message': 'User is unauthorized'}


