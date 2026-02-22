import contextlib

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from app.core.config import settings
from app.core.db import get_async_session
from app.core.logger import get_logger
from app.core.user import get_user_db, get_user_manager
from app.schemas.user import UserCreate


logger = get_logger(__name__)

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
        email: EmailStr,
        password: str,
        is_superuser:
        bool = False
):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser
                        )
                    )
                    logger.info(
                        f'✅ Успешно создан суперпользователь с email: {email}'
                    )
    # except UserAlreadyExists:
    #     pass
    except UserAlreadyExists:
        logger.info(
            f'ℹ️ Суперпользователь с email {email} уже существует в БД'
        )
        return None

    except Exception as e:
        logger.error(
            f'❌ Ошибка создания суперпользователя с email {email}: {str(e)}'
        )
        raise


async def create_first_superuser():
    if (settings.first_superuser_email is not None and
            settings.first_superuser_password is not None):
        logger.info('🚀 Запуск создания суперпользователя...')
        await create_user(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            is_superuser=True,
        )
    else:
        logger.warning(
            '⚠️ Настройки первого суперпользователя не указаны в .env файле. '
            'Суперпользователь не будет создан автоматически.'
        )
