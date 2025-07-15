from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from api_yamdb.settings import ROLE_CHOICES, UserRoles


class CustomUser(AbstractUser):
    """Пользовательская модель User."""
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default=UserRoles.USER,
        verbose_name='Роль'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы'
            )
        ],
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия"
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )

    @property
    def is_user(self):
        return self.role == UserRoles.USER

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_superuser

    def clean(self):
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError(
                {
                    'username': 'Использовать имя "me" '
                    'в качестве username запрещено'
                }
            )

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
