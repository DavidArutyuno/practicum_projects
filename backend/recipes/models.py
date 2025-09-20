from django.conf import settings as s
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import CreatedModel


User = get_user_model()


class Tag(models.Model):
    """Модель тега для категоризации рецептов."""

    name = models.CharField(
        'Название',
        max_length=s.TAG_NAME_LIMIT,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=s.TAG_NAME_LIMIT,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def save(self, *args, **kwargs):
        """Автогенерация слага из названия."""
        if not self.slug:
            max_slug_length = self._meta.get_field('slug').max_length
            slugify_slug = slugify(self.name)[:max_slug_length]
            slug = slugify_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{slugify_slug}-{counter}"
                counter = counter + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель - справочник ингредиентов."""

    name = models.CharField(
        'Название',
        max_length=s.INGREDIENT_NAME_LIMIT,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=s.MEASUREMENT_UNIT_LIMIT
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(CreatedModel):
    """Модель рецепта с ингредиентами и тегами."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=s.RECIPE_NAME_LIMIT,
        db_index=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to=s.RECIPE_IMAGE_DIR
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (минуты)',
        validators=[MinValueValidator(1)]
    )
    short_link = models.CharField(
        'Короткая ссылка',
        max_length=s.LENGTH,
        unique=True,
        blank=True,
        help_text='Хэш-id для короткой ссылки рецепта'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        """
        Явная логика для генерации коротких ссылок.

        Проверяем, новый ли объект и генерируем короткую ссылку
        после сохранения.
        """
        is_new = self._state.adding

        super().save(*args, **kwargs)

        if is_new and not self.short_link:
            from core.utils import generate_short_hash
            self.short_link = generate_short_hash(self.id)
            self.save(update_fields=['short_link'])

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Связь ингредиента с рецептом и указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'


class Favorite(CreatedModel):
    """Избранные рецепты пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(CreatedModel):
    """Рецепты в корзине покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
