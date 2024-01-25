from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str = "postgres"
    port: int = 5432
    name: str = "billing_db"
    user: str = "admin"
    password: str = "123qwe"

    model_config = SettingsConfigDict(env_prefix="db_", env_file=".env")


class Setting(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    dsn: str = f'postgresql+asyncpg://{postgres.user}:{postgres.password}@{postgres.host}:{postgres.port}/{postgres.name}'
    yookassa_token: str
    yookassa_shopid: str
    webhook_api_url: str


settings = Setting()
