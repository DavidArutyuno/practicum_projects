import base64
import hashlib

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле для обработки изображений в формате base64.

    Декодирует строку base64 в бинарные данные изображения и преобразует
    в объект ContentFile для дальнейшей обработки Django.

    Ожидает строку в формате: 'data:image/<format>;base64,<encoded_data>'
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'temp.{ext}'
            )
        return super().to_internal_value(data)


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
