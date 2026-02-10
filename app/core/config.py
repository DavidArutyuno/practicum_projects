from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения QRKot."""
    app_title: str = 'Благотворительный фонд поддержки котиков'
    description: str = 'Сервис для поддержки котиков'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()