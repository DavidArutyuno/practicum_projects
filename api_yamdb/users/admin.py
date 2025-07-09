"""
Добавление пользовательской модели CustomUser в админ-панель Django.

- добавляем поле с биографией к стандартному набору полей (fieldsets)
пользователя в админке.
- добавляем кортеж, где
    первый элемент — это название раздела в админке,
    второй элемент — словарь, где под ключом fields можно указать нужные поля.
- добавляем поле с биографией в список отображаемых в админке (list_display).
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser

""""Настройка раздела для пользователей и групп."""
admin_site = admin.site
admin_site.site_header = "Панель администратора"
admin_site.index_title = "Администрирование сайта"


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio',)}),
)
UserAdmin.list_display += ('bio',)


class GroupAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Group, GroupAdmin)
