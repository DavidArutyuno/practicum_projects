from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = "%Y/%m/%d %H:%M:%S"

SPREADSHEET_BODY = {
    'properties': {
        'locale': 'ru_RU'
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': 100,
                'columnCount': 11
            }
        }
    }]
}

PERMISSIONS_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email
}

UPDATE_BODY = {
    'majorDimension': 'ROWS'
}

TABLE_HEADERS = [
    ['Отчёт от ', '{now_date_time}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


async def create_spreadsheets(wrapper_services: Aiogoogle) -> str:
    """Функция создания таблицы."""
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = SPREADSHEET_BODY.copy()
    now_date_time = datetime.now().strftime(FORMAT)
    spreadsheet_body['properties']['title'] = f'Отчёт от {now_date_time}'

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """
    Функция для предоставления прав доступа
    личному аккаунту к созданному документу.

    Должна принимать строку с ID документа,
    на который надо дать права доступа,
    и экземпляр класса Aiogoogle.
    """
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=PERMISSIONS_BODY,
            fields='id'
        )
    )


async def update_spreadsheets_value(
        spreadsheet_id: str,
        charity_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = TABLE_HEADERS.copy()
    table_values[0][1] = datetime.now().strftime(FORMAT)

    for project in charity_projects:
        new_row = [
            str(project['name']),
            str(project['days_to_complete']),
            str(project['description'])
        ]
        table_values.append(new_row)

    update_body = UPDATE_BODY.copy()
    update_body['values'] = table_values

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
