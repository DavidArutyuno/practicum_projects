from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Title(models.Model):
    """
    Модель произведения.

    Поля:
        - name (str): Название произведения.
        - year (int): Год создания произведения.
        - description (str): Описание произведения (необязательно).
    """
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год создания')
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title_year',
            ),
        ]
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name
