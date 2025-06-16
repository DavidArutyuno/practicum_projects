from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response

from posts.models import Comment, Group, Post
from .serializers import (
    CommentSerializer, GroupSerializers, PostSerializer
)


class GroupList(generics.ListAPIView):
    """
    (GET): получаем список всех групп.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializers


class GroupDetail(generics.RetrieveAPIView):
    """
    (GET): получаем информацию о группе с идентификатором {group_id}.
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super(PostViewSet, self).perform_destroy(instance)


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

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        new_queryset = Comment.objects.filter(post_id=post_id)
        return new_queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_create(self, serializer):
    #     queryset = Post.objects.select_related(
    #         'comments').filter(user=self.request.user)

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        # super(CommentViewSet, self).perform_update(serializer)
        self.object = self.perform_create(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super(CommentViewSet, self).perform_destroy(instance)
