from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Пользовательская модель для пользователей."""
    verbose_name = 'Управление пользователями'
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        blank=False,
        null=False
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    ]
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __init__(self, *args, **kwargs):
        kwargs.pop('email', None)
        role = None
        if kwargs.pop('moderator', False):
            role = 'moderator'
        if kwargs.pop('admin', False):
            role = 'admin'
        if role:
            kwargs['role'] = role
        super().__init__(*args, **kwargs)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
