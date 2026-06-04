from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # ГЛАВНАЯ: список постов
    path(
        '',
        views.PostListView.as_view(),
        name='index'
    ),

    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts'
    ),

    # ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ

    # Просмотр
    path(
        'profile/<str:username>/',
        views.ProfilePostListView.as_view(),
        name='profile'
    ),

    # Редактирование
    path(
        'edit_profile/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),

    # ПОСТЫ

    # Создать
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),

    # Просмотр конкретного поста
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),

    # Редактировать
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),

    # Удалить
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),



    # КОММЕНТАРИИ

    # Добавить
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),

    # Редактировать
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),

    # Удалить
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]
