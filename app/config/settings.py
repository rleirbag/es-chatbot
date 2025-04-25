from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    model_config = SettingsConfigDict(env_file='.env')

    DATABASE_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_DOMAIN: str
    GOOGLE_FOLDER_NAME: str
