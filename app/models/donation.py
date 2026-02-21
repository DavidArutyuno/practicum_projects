"""Модель Donation."""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CharityBase


class Donation(CharityBase):
    """
    Модель «Пожертвование» (Donation).

    Каждый объект этой модели хранит данные об отдельном пожертвовании.
    """

    comment = Column(String)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=True
    )
