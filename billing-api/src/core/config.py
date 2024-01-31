from pydantic_settings import BaseSettings, SettingsConfigDict
from async_fastapi_jwt_auth import AuthJWT


class AuthJWTSettings(BaseSettings):
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_secret_key: str = 'some_key'


@AuthJWT.load_config
def get_auth_settings() -> AuthJWTSettings:
    return AuthJWTSettings()


class PostgresSettings(BaseSettings):
    host: str = "postgres"
    port: int = 5433
    name: str = "billing_db"
    user: str = "admin"
    password: str = "123qwe"

    model_config = SettingsConfigDict(env_prefix="db_", env_file=".env")


class CelerySettings(BaseSettings):
    broker_url: str

    model_config = SettingsConfigDict(env_prefix="celery_", env_file=".env")


class Setting(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    celery: CelerySettings = CelerySettings()
    dsn: str = f'postgresql+asyncpg://{postgres.user}:{postgres.password}@{postgres.host}:{postgres.port}/{postgres.name}'
    dsn_sync: str = f'postgresql://{postgres.user}:{postgres.password}@{postgres.host}:{postgres.port}/{postgres.name}'
    yookassa_token: str
    yookassa_shopid: str
    webhook_api_url: str
    payment_redirect_url: str

    AUTH_API_SUBSCRIBE_URL: str = "http://localhost/api/v1/users/subscribe"
    AUTH_API_UNSUBSCRIBE_URL: str = "https://localhost/api/v1/users/unsubscribe"

settings = Setting()
