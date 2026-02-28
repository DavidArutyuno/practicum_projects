from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.charity_project import charity_project_crud
from app.services import (
    create_spreadsheets, set_user_permissions, update_spreadsheets_value
)

router = APIRouter()


@router.post(
    '/',
    response_model=list[dict[str, int]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)

):
    """Только для суперюзеров."""
    projects = (
        await charity_project_crud.get_projects_by_completion_rate(session)
    )

    spreadsheetid = await create_spreadsheets(wrapper_services)
    await set_user_permissions(spreadsheetid, wrapper_services)
    await update_spreadsheets_value(spreadsheetid,
                                    projects,
                                    wrapper_services)
    return projects
