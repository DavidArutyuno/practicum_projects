from django.contrib import admin

from reviews import models


@admin.register(models.Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name', 'year',)
    empty_value_display = '-пусто-'
