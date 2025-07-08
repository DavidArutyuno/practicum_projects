from rest_framework import serializers
from django.utils import timezone

from reviews import models


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Поля сериализуемой модели:
        - name (str): Название произведения (обязательное поле).
        - year (int): Год создания произведения (обязательное поле,
            не может быть в будущем).
        - description (str): Описание произведения (необязательное поле).

    Методы:
        - validate_year: Проверяет, что год не больше текущего года.
    """
    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'description')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError("Год не может быть в будущем")
        return value
