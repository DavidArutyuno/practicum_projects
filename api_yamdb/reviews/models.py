from django.contrib.auth import get_user_model
from django.db import models

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
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(NameBaseModel):
    """
    Модель произведения.

    Поля:
        - name (str): Название произведения.
        - year (int): Год создания произведения.
        - description (str): Описание произведения (необязательно).
        - category (Category): Категория произведения.
    """
    year = models.IntegerField(verbose_name='Год создания')
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['name', 'year']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title_year',
            ),
        ]
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
