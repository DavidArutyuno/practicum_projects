"""Pydantic схемы пожертвований."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    """Для обычного пользователя (GET /donation/my)."""
    id: int
    create_date: datetime
    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """
    Полная информация о пожертвовании (только для суперпользователя).
    (GET /donation/).
    """
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
    user_id: Optional[int] = Field(None)

    model_config = ConfigDict(from_attributes=True)
