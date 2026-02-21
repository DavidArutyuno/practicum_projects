"""Подключение к БД."""
from sqlalchemy import Integer, MetaData
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, declared_attr
)

from app.core.config import settings


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Base(DeclarativeBase):
    """Базовый класс от которого будем наследовать все модели проекта."""

    metadata = MetaData(naming_convention=convention)


class CommonMixin:
    """
    Применение миксина позволит создавать разные модели — «чистые»,
    унаследованные только от Base, или «с примесями» — унаследованные
    от миксина и Base: class NewModel(CommonMixin, Base).
    """

    @declared_attr
    def __tablename__(cls):
        """
        Имя таблицы будет создано из названия модели в нижнем регистре,
        а во все таблицы будет добавлено поле ID.
        """
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    """
    Dependency для получения асинхронной сессии базы данных.

    При каждом вызове get_async_session()
    из AsyncSessionLocal извлекается сессия и возвращается
    тому, кто её запросил.

    Когда HTTP-запрос отработает - выполнение кода вернётся сюда;
        контекстный менеджер завершит работу;
        при завершении работы контекстного менеджера
        сессия будет автоматически закрыта.
    """
    async with AsyncSessionLocal() as async_session:
        yield async_session
