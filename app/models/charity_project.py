from sqlalchemy import Column, String, Text

from app.models.base import CharityBase


class CharityProject(CharityBase):
    """Модель «Проект» (CharityProject) описывает целевые проекты."""
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)