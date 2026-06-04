from django.conf import settings as s
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя с расширенными полями.

    Наследует все поля от AbstractUser и добавляет:
    - Обязательный email с проверкой уникальности
    - Поля имени и фамилии
    - Аватар пользователя
    """

    email = models.EmailField(
        unique=True,
        max_length=s.USER_EMAIL_LIMIT,
        verbose_name='Email адрес'
    )
    first_name = models.CharField(
        max_length=s.USER_NAME_LIMIT,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=s.USER_NAME_LIMIT,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to=s.USER_AVATAR_DIR,
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f'{self.username} ({self.email})'


class Subscription(models.Model):
    """
    Система подписок между пользователями.

    Реализует симметричные отношения "многие-ко-многим"
    через промежуточную модель с дополнительными ограничениями.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user} → {self.author}'
