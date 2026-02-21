from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:
    """
    get() — получить объект по id;
    get_multi() — получить все объекты заданного класса;
    create() — создать новый объект;
    update() — обновить объект;
    remove() — удалить объект.
    """

    def __init__(self, model):
        """
        Инициализатор класса на вход принимает модель,
        с которой нужно выполнить операции.
        """
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """Универсальный метод для получения объекта по его id."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ):
        """Универсальный метод для получения всех объектов заданной модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: Optional[User] = None
    ):
        """Универсальный метод для добавления записи в базу."""
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """Универсальный метод для обновления записи по id."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        if (hasattr(db_obj, 'full_amount') and
                hasattr(db_obj, 'invested_amount')):
            if (db_obj.invested_amount >= db_obj.full_amount and
                    not db_obj.fully_invested):
                db_obj.fully_invested = True
                db_obj.close_date = datetime.now()

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Универсальный метод для удаления объекта."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
