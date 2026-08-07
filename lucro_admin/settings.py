from pydantic_settings import BaseSettings, SettingsConfigDict


class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 1800


class MeradoPagoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='mp.env', env_file_encoding='utf-8'
)

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str


class BlingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='bling.env',
        env_file_encoding='utf-8'
    )

    CLIENT_ID: str
    CLIENT_SECRET: str
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    EXPIRE: str


class MeliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='ml.env',
        env_file_encoding='utf-8'
    )

    CLIENT_ID: str
    CLIENT_SECRET: str
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    EXPIRE: str

