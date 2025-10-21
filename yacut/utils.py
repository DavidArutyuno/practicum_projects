import random
import string

from . import db
from .models import URLMap


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