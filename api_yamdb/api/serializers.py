from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

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
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=models.Genre.objects.all(),
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


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title в режиме чтения.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Title
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre', 'rating'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    Поля:
        - title: Название произведения (read_only, slug_field='name')
        - author: Имя пользователя (read_only, slug_field='username')
        - score: Оценка (валидируется, должна быть от 0 до 10)
        - Остальные поля соответствуют модели Review
    Валидация:
        - Оценка должна быть в диапазоне от 0 до 10
        - Один пользователь может оставить только один отзыв на произведение
    """
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        if not (0 <= value <= 10):
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 0 до 10.'
            )
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title_instance = get_object_or_404(models.Title, pk=title_id)
        if request.method == 'POST':
            existing_review = models.Review.objects.filter(
                title=title_instance,
                author=user
            )
            if existing_review.exists():
                raise serializers.ValidationError(
                    'Пользователь может оставить только один отзыв на '
                    'данное произведение.'
                )
        return attrs

    class Meta:
        model = models.Review
        fields = '__all__'


class ReviewReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review в режиме чтения.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = models.Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    Поля:
        - review: Текст отзыва, к которому относится комментарий
          (read_only, slug_field='text')
        - author: Имя пользователя (read_only, slug_field='username')
        - Остальные поля соответствуют модели Comment
    """
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = models.Comment


class CommentReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment в режиме чтения.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = models.Comment
        fields = ('id', 'text', 'author', 'pub_date')
