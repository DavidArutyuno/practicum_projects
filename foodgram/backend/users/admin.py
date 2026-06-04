"""
Административная панель для моделей приложения users.

Регистрирует модель User и связанные модели
для управления через Django admin interface.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import Subscription


User = get_user_model()


class SubscriptionInline(admin.TabularInline):
    """Inline для отображения подписок пользователя."""

    model = Subscription
    fk_name = 'user'
    extra = 0
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки пользователя'
    readonly_fields = ('author',)


class SubscriberInline(admin.TabularInline):
    """Inline для отображения подписчиков пользователя."""

    model = Subscription
    fk_name = 'author'
    extra = 0
    verbose_name = 'Подписчик'
    verbose_name_plural = 'Подписчики пользователя'
    readonly_fields = ('user',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомный административный класс для модели пользователя."""

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': settings.USER_EXTRA_FIELDS}),
    )
    list_display = settings.USER_LIST_DISPLAY
    list_display_links = settings.USER_LIST_DISPLAY_LINKS
    list_filter = settings.USER_LIST_FILTER
    search_fields = settings.USER_LIST_FILTER
    list_editable = settings.USER_LIST_EDITABLE
    empty_value_display = settings.EMPTY_VALUE_DISPLAY

    inlines = [SubscriptionInline, SubscriberInline]


# Настройка админ-панели
admin.site.site_header = settings.SITE_HEADER
admin.site.index_title = settings.INDEX_TITLE

# Убираем стандартные модели
admin.site.unregister(Group)
