"""Эндпоинты для пожертвований."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investments import invest_in_project

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: SessionDep,
):
    """Показать список всех пожертвований."""
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
):
    """Создать пожертвование."""
    new_donation = await invest_in_project(
        donation, session, is_donation=True
    )
    return new_donation