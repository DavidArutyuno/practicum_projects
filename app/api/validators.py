from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_charity_project_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    """Проверяет уникальность имени проекта."""
    project_id = await charity_project_crud.get_project_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет существование проекта по ID."""
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return charity_project


async def check_project_invested_amount(
    project_id: int,
    new_full_amount: int,
    session: AsyncSession,
) -> None:
    """Проверяет, что новая сумма не меньше уже инвестированной."""
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if new_full_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='Нельзя установить значение full_amount меньше уже вложенной суммы.'
        )


async def check_project_before_update(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет возможность обновления проекта."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project


async def check_project_before_delete(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет возможность удаления проекта."""
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return charity_project