from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Deferrable
from django.db.models.constraints import UniqueConstraint


User = get_user_model()


class Group(models.Model):
    """Описание модели сообществ."""
    title = models.CharField(
        max_length=200,
        verbose_name='Название сообщества',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Тег',
    )
    description = models.TextField(verbose_name='Описание',)

    class Meta:
        verbose_name = 'сообщество'
        verbose_name_plural = 'Список сообществ'

    def __str__(self):
        return self.title


class Follow(models.Model):
    """Описание модели подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Кто подписан',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписан',
        help_text=(
            'Нельзя подписаться на самого себя. '
            'Нельзя подписаться дважды на одного пользователя.'
        )
    )

    class Meta:
        """
        Constraints (ограничения).

        Добавлен параметр deferrable=Deferrable.DEFERRED, который позволяет
        отложить проверку уникальности до конца транзакции.
        Это особенно полезно при работе с большими наборами данных или сложными
        операциями, где временное нарушение уникальности не вызывает проблем,
        а проверка в конце гарантирует целостность данных.
        """
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ["following", "user"]
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow',
                deferrable=Deferrable.DEFERRED
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class Post(models.Model):
    """Описание модели публикаций."""
    text = models.TextField('Текст публикации')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Название сообщества',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Описание модели комментариев."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    text = models.TextField('Текст комментария',)
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
