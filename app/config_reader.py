from pydantic import BaseModel, BaseSettings


class PostgresSettings(BaseModel):
    host: str
    port: int
    login: str
    password: str
    db: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.login}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseModel):
    host: str
    port: int
    password: str

    @property
    def url(self) -> str:
        return f"redis://default:{self.password}@{self.host}:{self.port}"


class WebhookSettings(BaseModel):
    host: str
    path: str

    @property
    def url(self) -> str:
        return f"https://{self.host}{self.path}"


class Settings(BaseSettings):
    bot_token: str
    bot_admin: int
    postgres: PostgresSettings
    redis: RedisSettings
    webhook: WebhookSettings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


config = Settings()
