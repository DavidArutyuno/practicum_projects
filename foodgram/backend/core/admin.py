from django.conf import settings
from django.contrib import admin
from django.contrib.admin import display


class GetAuthorMixin(admin.ModelAdmin):
    """Повторяющийся блок кода вынесен в общий миксин."""

    list_display = settings.FS_LIST_DISPLAY
    list_display_links = settings.FS_LIST_DISPLAY_LINKS
    list_filter = settings.FS_LIST_FILTER
    search_fields = settings.FS_SEARCH_FIELDS
    empty_value_display = settings.EMPTY_VALUE_DISPLAY

    @display(description='Автор рецепта')
    def get_author(self, obj):
        return obj.recipe.author
