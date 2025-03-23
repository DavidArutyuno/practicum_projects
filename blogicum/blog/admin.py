from django.contrib import admin


from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    """
    Кастомный класс админки.

    Создаём класс, в котором будем описывать настройки админки
    """

    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    # Вместо пустого значения будет выводиться строка "Не задано".
    empty_value_display = 'Не задано'
    # Указываем, для каких связанных моделей нужно включить такой интерфейс:
    # filter_horizontal = ('category',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Location)
