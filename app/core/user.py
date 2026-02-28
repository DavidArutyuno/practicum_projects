from typing import Annotated, Optional, Union

from fastapi import Depends, Request

from fastapi_users import (
    BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.logger import get_logger
from app.models.user import User
from app.schemas.user import UserCreate


MIN_PASSWORD_LENGTH = 3
JWT_TOKEN_LIFETIME_SECONDS = 3600  # 1 час

logger = get_logger(__name__)


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    yield SQLAlchemyUserDatabase(session, User)

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret,
        lifetime_seconds=JWT_TOKEN_LIFETIME_SECONDS
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    WARNING_TEMPLATE = '⚠️ Валидация пароля провалена для %s: %s'

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:

        password_length = len(password)

        if password_length < MIN_PASSWORD_LENGTH:
            error_msg = (
                f'Пароль должен содержать не менее {MIN_PASSWORD_LENGTH} '
                f'символов (сейчас {password_length})'
            )
            logger.warning(
                self.WARNING_TEMPLATE,
                user.email,
                error_msg
            )
            raise InvalidPasswordException(reason=error_msg)

        if user.email in password:
            error_msg = 'Пароль не может содержать ваш email'
            logger.warning(
                self.WARNING_TEMPLATE,
                user.email,
                error_msg
            )
            raise InvalidPasswordException(reason=error_msg)

        logger.debug('Пароль для %s успешно прошёл валидацию', user.email)

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None
    ):
        """Действия после регистрации."""
        logger.info('✅ Новый пользователь зарегистрирован: ID=%s', user.id)
        logger.info('✅ Email: %s', user.email)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Корутина, возвращающая объект класса UserManager."""
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
