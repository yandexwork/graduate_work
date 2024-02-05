from pydantic_settings import BaseSettings, SettingsConfigDict


class BillingClientSettings(BaseSettings):
    base_url: str = "http://nginx:81/billing-api/v1"
    subscribe_path: str = "/subscribe"
    tariff_path: str = "/tariffs"

    model_config = SettingsConfigDict(env_prefix="billing_client_", env_file=".env")


class AuthClientSettings(BaseSettings):
    base_url: str = "https://fb1d-46-138-13-33.ngrok-free.app/api/v1"
    login: str = 'admin'
    password: str = 'admin'
    login_path: str = "/auth/login"

    model_config = SettingsConfigDict(env_prefix="billing_client_", env_file=".env")


billing_client_settings = BillingClientSettings()
auth_client_settings = AuthClientSettings()
