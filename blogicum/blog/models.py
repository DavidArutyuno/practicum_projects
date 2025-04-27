from django.contrib.auth import get_user_model
from django.db import models
# Импортируем функцию reverse() для получения ссылки на объект.
from django.urls import reverse
from django.utils import timezone as dt

from blogicum import settings as s
from core.models import PublishedModel


User = get_user_model()


class Category(PublishedModel):
    """Тематическая категория."""

    title = models.CharField(
        max_length=s.MAX_LENGTH_CHAR,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        max_length=s.MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:s.RIGHT_TRIM]


class Location(PublishedModel):
    """Географическая метка."""

    name = models.CharField(
        max_length=s.MAX_LENGTH_CHAR,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:s.RIGHT_TRIM]


class Post(PublishedModel):
    """
    Публикация.

    Главное в блоге — это публикация («пост»), вокруг неё всё и строится.
    """

    title = models.CharField(
        max_length=s.MAX_LENGTH_CHAR,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=False,
        default=dt.now,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        null=True,
        related_name='posts'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        # blank=False,
        verbose_name='Категория'
    )
    image = models.ImageField('Изображение', upload_to='posts/', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pk',)
        default_related_name = 'posts'

    def get_absolute_url(self):
        # С помощью функции reverse() возвращаем URL объекта.
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title[:s.RIGHT_TRIM]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
        related_name='post_comments',
        verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    # def get_absolute_url(self):
    #     return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.text
