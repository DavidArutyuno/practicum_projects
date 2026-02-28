from sqlalchemy import Column, Integer, String, Text

from app.models.base import CharityBase


class CharityProject(CharityBase):
    """Модель «Проект» (CharityProject) описывает целевые проекты."""

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    days_to_complete = Column(
        Integer,
        nullable=True,
        comment='Кол-во дней на сбор средств'
    )
