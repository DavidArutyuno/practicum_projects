from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings


description = f'{settings.description}'
app = FastAPI(
    title=settings.app_title,
    description=description
)

app.include_router(main_router)
