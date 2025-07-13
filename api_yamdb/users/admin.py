"""
Добавление пользовательской модели CustomUser в админ-панель Django.

- добавляем поля (bio, role) к стандартному набору полей (fieldsets)
пользователя в админке.
- добавляем кортеж, где
    первый элемент — это название раздела в админке,
    второй элемент — словарь, где под ключом fields можно указать нужные поля.
- добавляем поля (bio, role) в список отображаемых в админке (list_display).
- добавляем поле (role) в список фильтрующихся в админке (list_filter).
- добавляем поле (role) в список редактируемых в админке (list_editable).
- добавляем на будущее возможность кастомизации заголовков в админке.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


User = get_user_model()


""""Настройка раздела для пользователей и групп."""
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio', 'role',)}),
)
UserAdmin.list_display += ('bio', 'role',)
UserAdmin.list_filter += ('role',)
UserAdmin.list_editable = ('role',)

admin_site = admin.site
admin_site.site_header = "Панель администратора"
admin_site.index_title = "Администрирование сайта"
admin_site.register(User, UserAdmin)
admin_site.unregister(Group)
