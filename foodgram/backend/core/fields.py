import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
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
