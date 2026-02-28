"""CRUD операции для целевых проектов."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_name
            )
        )
        return project.scalars().first()

    async def get_open_projects(
        self,
        session: AsyncSession,
    ):
        open_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        return open_projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
