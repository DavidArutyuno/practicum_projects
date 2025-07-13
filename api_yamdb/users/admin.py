"""
Настройка пользовательской модели CustomUser в админ-панели Django.

- Добавление полей bio и role к стандартным полям пользователя
- Настройка отображения, фильтрации и редактирования полей
- Кастомизация заголовков админ-панели
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """Кастомный административный класс для модели пользователя."""

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': ('bio', 'role')}),
    )
    list_display = UserAdmin.list_display + ('bio', 'role')
    list_filter = UserAdmin.list_filter + ('role',)
    list_editable = ('role',)


# Настройка админ-панели
admin.site.site_header = "Панель администратора"
admin.site.index_title = "Администрирование сайта"

# Регистрация моделей
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
