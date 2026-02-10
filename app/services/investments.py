"""
Функции, отвечающие за инвестирование, вызываются непосредственно
из API-функций, отвечающих за создание пожертвований и целевых проектов.
"""

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


async def execute_investment_process(
    session: AsyncSession,
) -> None:
    """
    Функция распределяет неинвестированные пожертвования по открытым проектам.
    project_remaining - доступные суммы.
    investment_amount - сумма для инвестирования.
    """
    open_projects = await charity_project_crud.get_open_projects(session)
    open_donations = await donation_crud.get_open_donations(session)

    if not open_projects or not open_donations:
        return

    project_index = 0
    donation_index = 0

    while (
        project_index < len(open_projects) and
        donation_index < len(open_donations)
    ):
        project = open_projects[project_index]
        donation = open_donations[donation_index]

        project_remaining = project.full_amount - project.invested_amount
        donation_remaining = donation.full_amount - donation.invested_amount

        investment_amount = min(project_remaining, donation_remaining)

        project.invested_amount += investment_amount
        donation.invested_amount += investment_amount

        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            project_index += 1

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            donation_index += 1

        session.add(project)
        session.add(donation)

    await session.commit()


async def invest_in_project(
    obj_in,
    session: AsyncSession,
    is_donation: bool = False,
) -> Tuple[Optional[CharityProject], Optional[Donation]]:
    """
    Универсальная функция для создания объекта и запуска процесса инвестирования.
    """
    if is_donation:
        db_obj = await donation_crud.create(obj_in, session)
    else:
        db_obj = await charity_project_crud.create(obj_in, session)

    await execute_investment_process(session)
    await session.refresh(db_obj)
    return db_obj