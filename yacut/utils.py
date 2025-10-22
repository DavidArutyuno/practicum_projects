import random
import string

from . import app, db
from .models import URLMap


BASE_URL = app.config.get('BASE_URL')


def get_unique_short_id():
    """
    Генерирует случайный короткий идентификатор переменной длины.
    EXISTS запрос будет эффективнее для больших баз.
    """
    length = 6
    characters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(characters) for _ in range(length))

        exists = db.session.query(
            URLMap.query.filter_by(short=short_id).exists()
        ).scalar()
        if not exists:
            return short_id


def merge_links_dicts(links_list):
    """Объединяет список словарей в один словарь."""
    result = {}
    for links_dict in links_list:
        result.update(links_dict)
    return result


def create_short_links_for_files(file_links_dict):
    """
    Создает короткие ссылки для каждого файла.
    """
    short_links = {}

    for filename, original_link in file_links_dict.items():
        short_id = get_unique_short_id()

        # Создаем запись в базе
        url_map = URLMap(original=original_link, short=short_id)
        db.session.add(url_map)

        # Формируем короткую ссылку
        short_link = f'{BASE_URL}/{short_id}'
        short_links[filename] = short_link

    # Коммитим все изменения одним запросом
    db.session.commit()

    return short_links
