import time
import urllib
import aiohttp
import asyncio

from . import app


# Словарь с заголовком авторизации.
AUTH_HEADERS = {
    'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'
}

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

# Эндпоинт для запроса на получение URL для загрузки файла
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'

# Эндпоинт для запроса ссылки на скачивание файла с Диска
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def async_upload_files_to_YaDISK(images):
    """
    Асинхронная функция, которая создаёт задачи и запускает их.
    """
    if images is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for image in images:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, image)
                    )
                )
            links = await asyncio.gather(*tasks, return_exceptions=True)
        return links


async def upload_file_and_get_url(session, image):
    """
    Асинхронно загружает один файл и возвращает ссылку.
    """
    start_time = time.time()
    filename = image.filename
    # filename = urllib.parse.quote(image.filename, safe='')

    path = f'app:/{filename}'

    try:
        print(f'Начало загрузки {filename}')

        # 1. Получаем URL для загрузки
        async with session.get(
            REQUEST_UPLOAD_URL,
            headers=AUTH_HEADERS,
            params={'path': path, 'overwrite': 'true'}
        ) as response:
            if response.status != 200:
                print(
                    f'Ошибка получения upload URL для {filename}: {response.status}')
                return {}
            data = await response.json()
            upload_url = data.get('href')

        if not upload_url:
            print(f'Не получили upload URL для {filename}')
            return {}

        # 2. Загружаем файл
        image.seek(0)
        file_data = image.read()

        async with session.put(upload_url, data=file_data) as response:
            if response.status not in [201, 202]:
                print(f'Ошибка загрузки {filename}: {response.status}')
                return {}

        # 3. Получаем ссылку для скачивания
        async with session.get(
            DOWNLOAD_LINK_URL,
            headers=AUTH_HEADERS,
            params={'path': path}
        ) as response:
            if response.status != 200:
                print(f'Ошибка получения ссылки для {filename}: '
                      '{response.status}')
                return {}
            data = await response.json()
            download_link = urllib.parse.unquote(data.get('href'))

        if download_link:
            filename = urllib.parse.unquote(image.filename)
            print(f'Успешно: {filename} -> {download_link}')
            print('Итоговое время загрузки', time.time() - start_time)
            return {filename: download_link}
        else:
            return {}

    except Exception as e:
        print(f"Ошибка при обработке {filename}: {e}")
        return {}
