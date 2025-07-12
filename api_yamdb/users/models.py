from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Пользовательская модель User."""
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    ]
    role = models.CharField(
        'Роль',
        max_length=15,
        choices=ROLE_CHOICES,
        default='user'
    )
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
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __init__(self, *args, **kwargs):
        moderator_flag = kwargs.pop('moderator', False)
        admin_flag = kwargs.pop('admin', False)

        super().__init__(*args, **kwargs)

        if moderator_flag:
            self.role = 'moderator'
        if admin_flag:
            self.role = 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
