"""CRUD операции для пожертвований."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation


class CRUDDonation(CRUDBase):
    async def get_open_donations(
        self,
        session: AsyncSession,
    ):
        open_donations = await session.execute(
            select(Donation).where(
                Donation.fully_invested == False
            ).order_by(Donation.create_date)
        )
        return open_donations.scalars().all()


donation_crud = CRUDDonation(Donation)