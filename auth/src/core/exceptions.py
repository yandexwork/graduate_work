from http import HTTPStatus


class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code


class ErrorMessagesUtil:

    # Роли

    @staticmethod
    def roles_not_found():
        return f"Roles not found."

    @staticmethod
    def role_not_found():
        return f"Role not found."

    @staticmethod
    def role_already_exist():
        return f"Role already exist"

    @staticmethod
    def user_doesnt_have_this_role():
        return f"User does not have this role."

    @staticmethod
    def user_does_not_exist():
        return f"User does not exist"

    @staticmethod
    def user_does_not_have_rights():
        return f"User does not have rights for that action"

    # Пользователи

    @staticmethod
    def user_not_found():
        return f"User not found."

    @staticmethod
    def user_already_exists():
        return f"User already exists."

    @staticmethod
    def wrong_password():
        return f"Wrong password given."

    @staticmethod
    def password_is_weak():
        return f"Password is weak."

    # Токены

    @staticmethod
    def unable_to_refresh_token():
        return f"Unable to refresh token."

    @staticmethod
    def access_token_is_invalid():
        return f"Access token is invalid."

    @staticmethod
    def refresh_token_is_invalid():
        return f"Refresh token is invalid."

    @staticmethod
    def user_not_authorized():
        return f"User not authorized."

    @staticmethod
    def oauth_error():
        return f"OAuth get an error"


USER_NOT_AUTHORIZED = CustomException(
    status_code=HTTPStatus.UNAUTHORIZED,
    message=ErrorMessagesUtil.user_not_authorized()
)

USER_NOT_FOUND = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.user_not_found()
)

ACCESS_TOKEN_IS_INVALID = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.access_token_is_invalid()
)

WRONG_PASSWORD = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.wrong_password()
)

REFRESH_TOKEN_IS_INVALID = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.refresh_token_is_invalid()
)

USER_ALREADY_EXIST = CustomException(
    status_code=HTTPStatus.CONFLICT,
    message=ErrorMessagesUtil.user_already_exists()
)

ROLE_NOT_FOUND = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.role_not_found()
)

USER_DOES_NOT_HAVE_RIGHTS = CustomException(
    status_code=HTTPStatus.FORBIDDEN,
    message=ErrorMessagesUtil.user_does_not_have_rights()
)

USER_DOES_NOT_HAVE_ROLE = CustomException(
    status_code=HTTPStatus.NOT_FOUND,
    message=ErrorMessagesUtil.user_doesnt_have_this_role()
)

ROLE_ALREADY_EXIST = CustomException(
    status_code=HTTPStatus.CONFLICT,
    message=ErrorMessagesUtil.role_already_exist()
)

OAUTH_ERROR = CustomException(
    status_code=HTTPStatus.BAD_REQUEST,
    message=ErrorMessagesUtil.oauth_error()
)
