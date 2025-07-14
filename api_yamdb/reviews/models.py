from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import REVIEW_MAX_SCORE, REVIEW_MIN_SCORE

User = get_user_model()


class SlugBaseModel(models.Model):
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Слаг')

    class Meta:
        abstract = True


class NameBaseModel(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Category(NameBaseModel, SlugBaseModel):
    """
    Модель категории.

    Поля:
        - name (str): Название категории.
        - slug (str): Слаг категории.
    """

    class Meta:
        # ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameBaseModel, SlugBaseModel):
    """
    Модель жанра.

    Поля:
        - name (str): Название жанра.
        - slug (str): Слаг жанра.
    """

    class Meta:
        # ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(NameBaseModel):
    """
    Модель произведения.

    Поля:
        - name (str): Название произведения.
        - year (int): Год создания произведения.
        - description (str): Описание произведения (необязательно).
        - category (Category): Категория произведения.
        - genre (Genre): Жанры произведения (many-to-many).
    """
    year = models.IntegerField(verbose_name='Год создания')
    description = models.TextField(
        verbose_name='Описание',
        default='',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        # ordering = ['name', 'year']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title_year',
            ),
        ]
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class GenreTitle(models.Model):
    """
    Промежуточная модель для связи Title и Genre.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    """
    Модель отзывов.

    Поля:
        - title (str):  связь с произведением (Title).
        - text — текст отзыва (ограничение 200 символов).
        - author — автор отзыва (User).
        - score — оценка (от 1 до 10).
        - pub_date — дата публикации.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='произведение'
    )
    text = models.TextField(
        max_length=2000
    )
    author = models.ForeignKey(
        User,
        related_name='review',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    score = models.IntegerField(
        'баллы',
        validators=[
            MinValueValidator(REVIEW_MIN_SCORE),
            MaxValueValidator(REVIEW_MAX_SCORE),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return f'{self.title.name} - {self.author.username}'


class Comment(models.Model):
    """
    Модель комментариев к отзывам.

    Поля:
        - review (Review): Связь с отзывом.
        - text (str): Текст комментария.
        - author (User): Автор комментария.
        - pub_date (datetime): Дата публикации.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author.username} - {self.review.title.name}'
