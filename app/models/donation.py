"""Модель Donation."""
from sqlalchemy import Column, String

from app.models.base import CharityBase


class Donation(CharityBase):
    """
    Модель «Пожертвование» (Donation).

    Каждый объект этой модели хранит данные об отдельном пожертвовании.
    """
    comment = Column(String)