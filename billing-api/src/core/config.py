from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str
    port: str
    name: str
    user: str
    password: str

    model_config = SettingsConfigDict(env_prefix="db_", env_file=".env")


class Setting(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    dsn: str = f'postgresql+asyncpg://{postgres.user}:{postgres.password}@{postgres.host}:{postgres.port}/{postgres.name}'


settings = Setting()
