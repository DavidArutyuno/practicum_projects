"""Эндпоинты для пожертвований."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investments import invest_in_project

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
UserDep = Annotated[User, Depends(current_user)]


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: SessionDep,
):
    """Показать список всех пожертвований (только для суперпользователя)."""
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
)
async def get_my_donations(
    session: SessionDep,
    user: UserDep,
):
    """Показать список своих пожертвований."""
    donations = await donation_crud.get_by_user(session, user)
    return donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: UserDep,
):
    """Создать новое пожертвование."""
    new_donation = await donation_crud.create(
        donation, session, user
    )
    await invest_in_project(new_donation, session, is_donation=True)
    return new_donation
