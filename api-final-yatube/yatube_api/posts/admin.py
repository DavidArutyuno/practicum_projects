"""Кастомизированные классы административной панели django."""

from django.contrib import admin

from .models import Comment, Group, Follow, Post


class CommentAdmin(admin.ModelAdmin):
    """
    Класс модели Comment с индивидуальными настройками админ-зоны.
    """
    list_display = (
        'pk',
        'author',
        'text',
        'created',
    )
    list_filter = ('author', 'created',)
    list_display_links = ('author',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """
    Класс модели модели Group с индивидуальными настройками админ-зоны.
    """
    list_display = (
        'title',
        'slug',
        'description',
    )

    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """
    Класс модели Follow с индивидуальными настройками админ-зоны.
    """
    list_display = ('user', 'following',)
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    """
    Класс модели Post с индивидуальными настройками админ-зоны.
    """

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('text', 'group',)
    search_fields = ('text',)
    list_filter = ('author', 'pub_date',)
    list_display_links = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Comment, CommentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Post, PostAdmin)
