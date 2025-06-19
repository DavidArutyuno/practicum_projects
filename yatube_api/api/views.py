from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from posts.models import Comment, Group, Post
from .serializers import (
    CommentSerializer, GroupSerializers, PostSerializer
)
from .permissions import IsAuthorOrReadOnly


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    (GET): получаем список всех групп или
        получаем информацию о группе с идентификатором {group_id}.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializers
    permission_classes = [IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    """
    Описание работы класса.

    (GET, POST): получаем список всех постов или создаём новый пост.
    (GET, PUT, PATCH, DELETE): получаем, редактируем или
        удаляем пост с идентификатором{post_id}.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticated]

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
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(
            author=self.request.user,
            post_id=post_id
        )
