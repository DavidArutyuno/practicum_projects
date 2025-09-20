import base64
import hashlib

from django.conf import settings


def generate_short_hash(obj_id, length=settings.LENGTH):
    """
    Генерирует короткий URL-safe хэш из ID объекта.

    Использует MD5 хэширование и base64 кодирование для создания
    короткого идентификатора. Убирает все не-буквенно-цифровые
    символы для обеспечения URL-безопасности.
    """

    hash_bytes = hashlib.md5(str(obj_id).encode()).digest()

    short_hash = base64.urlsafe_b64encode(hash_bytes).decode()

    short_hash = ''.join(c for c in short_hash if c.isalnum())[:length]

    return short_hash.lower()
