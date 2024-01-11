from async_fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config


class AuthJWTSettings(BaseSettings):
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_secret_key: str = 'some_key'


class Setting(BaseSettings):
    DB_URL: str
    REDIS_HOST: str
    REDIS_PORT: str
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    jaeger_agent_host_name: str
    jaeger_agent_port: int


class AdminSettings(BaseSettings):
    ADMIN_LOGIN: str
    ADMIN_PASSWORD: str
    ADMIN_FIRST_NAME: str
    ADMIN_LAST_NAME: str
    ADMIN_ROLE_NAME: str


class GoogleSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str


google_settings = GoogleSettings()


config_data = {
    'GOOGLE_CLIENT_ID': google_settings.GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': google_settings.GOOGLE_CLIENT_SECRET
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
oauth_services = {
    'google': oauth.google
}


@AuthJWT.load_config
def get_auth_settings() -> AuthJWTSettings:
    return AuthJWTSettings()


settings = Setting()
auth_jwt_settings = AuthJWTSettings()
admin_settings = AdminSettings()
