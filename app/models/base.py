"""Базовый класс моделей CharityProject и Donation."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer

from app.core.db import Base, CommonMixin


class CharityBase(CommonMixin, Base):
    """
    Общий родительский класс (абстрактный) для моделей CharityProject и
    Donation с набором одинаковых полей.
    """

    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id}, '
            f'full_amount={self.full_amount}, '
            f'invested_amount={self.invested_amount}, '
            f'fully_invested={self.fully_invested}'
            ')'
        )
