from rest_framework import serializers
from django.utils import timezone

from reviews import models


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Поля сериализуемой модели:
        - name (str): Название произведения (обязательное поле,
            не может быть длиннее 256 символов).
        - year (int): Год создания произведения (обязательное поле,
            не может быть в будущем).
        - description (str): Описание произведения (необязательное поле).
        - category (Category): Категория произведения (необязательное поле).
        - genre (Genre): Жанры произведения (необязательное поле).

    Методы:
        - validate_year: Проверяет, что год не больше текущего года.
    """
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=models.Category.objects.all(),
        required=False,
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=models.Genre.objects.all(),
        required=False,
        many=True,
    )

    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError('Год не может быть в будущем')
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Поля сериализуемой модели:
        - name (str): Название категории (обязательное поле,
            не может быть длиннее 256 символов).
        - slug (str): Слаг категории (обязательное поле,
            не может быть длиннее 50 символов).
    """
    class Meta:
        model = models.Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Поля сериализуемой модели:
        - name (str): Название жанра (обязательное поле,
            не может быть длиннее 256 символов).
        - slug (str): Слаг жанра (обязательное поле,
            не может быть длиннее 50 символов).
    """
    class Meta:
        model = models.Genre
        fields = ('name', 'slug')
