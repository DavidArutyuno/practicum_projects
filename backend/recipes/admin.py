"""
Административная панель для моделей приложения recipes.

Регистрирует модели Tag, Ingredient, Recipe и связанные модели
для управления через Django admin interface.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth import get_user_model

from core.admin import GetAuthorMixin
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)


User = get_user_model()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов рецептов."""

    list_display = settings.TAG_LIST_DISPLAY
    list_display_links = settings.RECIPE_LIST_DISPLAY_LINKS
    search_fields = settings.TAG_SEARCH_FIELDS
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""

    list_display = settings.INGREDIENT_LIST_DISPLAY
    list_display_links = settings.RECIPE_LIST_DISPLAY_LINKS
    search_fields = settings.INGREDIENT_SEARCH_FIELDS
    list_filter = settings.INGREDIENT_LIST_FILTER
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


class IngredientInRecipeInline(admin.TabularInline):
    """Инлайн для добавления ингредиентов в рецепт."""

    model = IngredientInRecipe
    extra = 1
    min_num = 1
    verbose_name = 'ингредиент'
    verbose_name_plural = 'Ингредиенты в рецепте'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов с подсчетом избранного."""

    list_display = settings.RECIPE_LIST_DISPLAY
    list_display_links = settings.RECIPE_LIST_DISPLAY_LINKS
    list_filter = settings.RECIPE_LIST_FILTER
    search_fields = settings.RECIPE_SEARCH_FIELDS
    readonly_fields = settings.RECIPE_READONLY_FIELDS
    filter_horizontal = settings.RECIPE_FILTER_HORIZONTAL
    inlines = (IngredientInRecipeInline,)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY

    @display(description='В избранном')
    def favorites_count(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorited_by.count()


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для связи ингредиентов и рецептов."""

    list_display = settings.IIR_LIST_DISPLAY
    list_display_links = settings.IIR_LIST_DISPLAY_LINKS
    list_filter = settings.IIR_LIST_FILTER
    search_fields = settings.IIR_SEARCH_FIELDS
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Favorite)
class FavoriteAdmin(GetAuthorMixin):
    """Админка для избранных рецептов."""


@admin.register(ShoppingCart)
class ShoppingCartAdmin(GetAuthorMixin):
    """Админка для корзины покупок."""
