"""
Функции, отвечающие за инвестирование, вызываются непосредственно
из API-функций, отвечающих за создание пожертвований и целевых проектов.
"""

from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


def remaining(obj) -> int:
    """
    Остаток.

    для проекта - сколько нужно собрать.
    для пожертвования - сколько можно потратить.
    """
    return obj.full_amount - obj.invested_amount


def invest_amount(obj, amount: int) -> None:
    """Инвестирует указанную сумму в объект."""
    obj.invested_amount += amount


async def close_if_complete(obj):
    """Закрывает объект и возвращает True, если он был закрыт."""
    if obj.invested_amount >= obj.full_amount and not obj.fully_invested:
        obj.fully_invested = True
        obj.close_date = datetime.now()
        return True
    return False


async def execute_investment_process(
    session: AsyncSession,
) -> None:
    """
    Распределяет пожертвования по проектам.

    need - сколько нужно проекту.
    have - сколько есть в пожертвовании.
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

        # Сколько нужно проекту и сколько есть в пожертвовании
        need = remaining(project)
        have = remaining(donation)

        # Вычисляем сумму инвестирования
        investment = min(need, have)

        # Инвестируем
        invest_amount(project, investment)
        invest_amount(donation, investment)

        # Проверяем закрытие
        if await close_if_complete(project):
            project_index += 1
        if await close_if_complete(donation):
            donation_index += 1

        session.add(project)
        session.add(donation)

    await session.commit()


async def invest_in_project(
    obj_in,
    session: AsyncSession,
    is_donation: bool = False,
) -> Union[CharityProject, Donation]:
    """
    Универсальная функция для создания объекта и
    запуска процесса инвестирования.
    """
    if not is_donation:
        # Для проектов - создаём новый
        db_obj = await charity_project_crud.create(obj_in, session)
    elif isinstance(obj_in, Donation):
        # Для пожертвований - обновляем существующее
        db_obj = obj_in
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
    else:
        # Для новых пожертвований
        db_obj = obj_in

    await execute_investment_process(session)

    if not isinstance(db_obj, Donation):
        await session.refresh(db_obj)

    return db_obj
