from pydantic_settings import BaseSettings

from server.enums import Environment


class AppConfig(BaseSettings):
    APP_NAME: str
    APP_ENV: Environment = Environment.LOCAL
    APP_VERSION: str = "0.0.0"
    FALLBACK_LOCALE: str = "en-US"
    LOCALE: str
    TIMEZONE: str


class Config:
    app = AppConfig()


config = Config()
