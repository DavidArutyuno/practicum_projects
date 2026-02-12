"""Эндпоинты для целевых проектов."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_exists,
    check_charity_project_name_duplicate,
    check_project_before_delete,
    check_project_before_update,
    check_project_invested_amount,
)
from app.core.db import get_async_session
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investments import invest_in_project

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: SessionDep,
):
    """Показать список всех целевых проектов."""
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep,
):
    """Создать целевой проект."""
    await check_charity_project_name_duplicate(
        charity_project.name, session
    )
    new_project = await invest_in_project(
        charity_project, session, is_donation=False
    )
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
):
    """
    Редактировать целевой проект.

    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )

    if obj_in.name is not None:
        await check_charity_project_name_duplicate(
            obj_in.name, session
        )

    charity_project = await check_project_before_update(
        project_id, session
    )

    if obj_in.full_amount is not None:
        await check_project_invested_amount(
            project_id, obj_in.full_amount, session
        )

    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )

    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep,
):
    """
    Удалить целевой проект.

    Нельзя удалить проект, в который уже были инвестированы средства.
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    charity_project = await check_project_before_delete(
        project_id, session
    )
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
