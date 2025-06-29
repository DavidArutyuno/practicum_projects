from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from api.mixins import CreateListViewSet
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CommentSerializer, FollowSerializer, GroupSerializers, PostSerializer
)
from posts.models import Comment, Follow, Group, Post, User


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    (GET): получаем список всех групп или
        получаем информацию о группе с идентификатором {group_id}.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializers


class PostViewSet(viewsets.ModelViewSet):
    """
    Описание работы класса.

    (GET, POST): получаем список всех постов или создаём новый пост.
    (GET, PUT, PATCH, DELETE): получаем, редактируем или
        удаляем пост с идентификатором{post_id}.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Описание работы класса.

    (GET): получаем список всех комментариев поста с  идентификатором post_id
    (POST): создаём новый комментарий для поста с идентификатором {post_id}.
    (GET, PUT, PATCH, DELETE): получаем, редактируем или
        удаляем комментарий с идентификатором {comment_id}
        в посте с  id=post_id.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(
            author=self.request.user,
            post_id=post_id
        )


class FollowViewSet(CreateListViewSet):
    """
    Описание работы класса.

    (GET): Возвращает все подписки пользователя, сделавшего запрос.
        Анонимные запросы запрещены.
    (POST): Подписка пользователя от имени которого сделан запрос на
        пользователя переданного в теле запроса.
        Анонимные запросы запрещены.
    """

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username', )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )
