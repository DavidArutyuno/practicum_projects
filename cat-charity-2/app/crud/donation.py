"""CRUD операции для пожертвований."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    async def get_open_donations(
        self,
        session: AsyncSession,
    ):
        open_donations = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        return open_donations.scalars().all()

    async def get_by_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> list[Donation]:
        """Возвращает все пожертвования пользователя."""
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[Donation]:
        """Для суперпользователя - все пожертвования."""
        donations = await session.execute(
            select(Donation).order_by(Donation.create_date)
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
