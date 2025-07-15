from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.mixins import EmailValidationMixin, UsernameValidationMixin
from reviews import models
from users.confirmation import get_confirmation_code, send_confirmation_code

User = get_user_model()


class SignupSerializer(
    EmailValidationMixin,
    UsernameValidationMixin,
    serializers.Serializer
):
    """Сериализация данных пользователя в процессе регистрации."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )

    def validate(self, attrs):
        """Проверка уникальности email и username."""
        email = attrs['email']
        username = attrs['username']

        users = User.objects.filter(Q(email=email) | Q(username=username))

        errors = {}
        for user in users:
            if user.username == username and user.email != email:
                errors['username'] = (
                    'Пользователь с таким username уже существует.'
                )
            if user.email == email and user.username != username:
                errors['email'] = 'Пользователь с таким email уже существует.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def save(self):
        """Создание или обновление пользователя."""
        email = self.validated_data['email']
        username = self.validated_data['username']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created:
            user.email = email

        user.confirmation_code = get_confirmation_code()
        user.save()
        send_confirmation_code(user.email, user.confirmation_code)

        return user


class TokenSerializer(serializers.Serializer):
    """
    Получение токена.

    Сериализация данных пользователя в процессе получения токена.
    Добавляем специальный код ошибки: code='not_found'.
    """
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь не найден'},
                code='not_found'
            )

        if not data.get('username') or not data.get('confirmation_code'):
            raise serializers.ValidationError(
                'Необходимо указать username и confirmation_code',
                code='required_fields'
            )

        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )
        data['user'] = user
        return data


class UserSerializer(
    UsernameValidationMixin,
    serializers.ModelSerializer
):
    """
    Сериализация данных в процессе создания и обновления
    пользователя администратором.
    """
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserReadOrPatchSerializer(
    UsernameValidationMixin,
    serializers.ModelSerializer
):
    """
    Сериализация данных для процесса чтения и
    частичного обновления профиля пользователя.
    """
    username = serializers.CharField(
        required=False,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=False,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(
        choices=settings.ROLE_CHOICES,
        required=False,
        error_messages={
            'invalid_choice': 'Неверная роль.'
            'Допустимые значения: user, moderator, admin'
        }
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class MeSerializer(
    UsernameValidationMixin,
    serializers.ModelSerializer
):
    """Сериализация данных для работы с собственным профилем."""
    username = serializers.CharField(
        required=False,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=False,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


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

    def validate(self, attrs):
        if 'category' in attrs:
            category = attrs.get('category')
            if category is None or not getattr(category, 'slug', None):
                raise serializers.ValidationError({
                    'category': (
                        'Слаг категории обязателен и не может быть пустым.'
                    )
                })
        if 'genre' in attrs:
            genres = attrs.get('genre')
            if not genres or any(
                not getattr(genre, 'slug', None) for genre in genres
            ):
                raise serializers.ValidationError({
                    'genre': (
                        'Слаг жанра обязателен и не может быть пустым.'
                    )
                })

        return attrs


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
