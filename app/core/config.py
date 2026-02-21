from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения QRKot."""

    app_title: str = 'Благотворительный фонд поддержки котиков'
    description: str = 'Сервис для поддержки котиков'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
