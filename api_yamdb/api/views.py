from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api import serializers
from api.mixins import BaseViewSet
from api.filter import TitleFilter
from api.permissions import (
    IsAdminOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from reviews import models


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title с поддержкой CRUD и подсчётом рейтинга.
    """
    queryset = models.Title.objects.all().annotate(
        rating=Avg('reviews__score')
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.TitleReadSerializer
        return serializers.TitleSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self.read_serializer_instance = (
            serializers.TitleReadSerializer(instance)
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        self.read_serializer_instance = (
            serializers.TitleReadSerializer(instance)
        )


class CategoryViewSet(
    BaseViewSet,
):
    """
    ViewSet для модели Category.

    Операции:
        - GET: Получение списка категорий.
        - POST: Создание новой категории.
        - DELETE: Удаление категории по slug.

    Поиск:
        - По полю 'name'.
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(
    BaseViewSet,
):
    """
    ViewSet для модели Genre.

    Операции:
        - GET: Получение списка жанров.
        - POST: Создание нового жанра.
        - DELETE: Удаление жанра по slug.

    Поиск:
        - По полю 'name'.
    """
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review с поддержкой CRUD.
    """
    serializer_class = serializers.ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.ReviewReadSerializer
        return serializers.ReviewSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(models.Title, pk=title_id)
        instance = serializer.save(author=self.request.user, title=title)
        self.read_serializer_instance = (
            serializers.ReviewReadSerializer(instance)
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        self.read_serializer_instance = (
            serializers.ReviewReadSerializer(instance)
        )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return models.Review.objects.filter(title_id=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Comment с поддержкой CRUD.
    """
    serializer_class = serializers.CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.CommentReadSerializer
        return serializers.CommentSerializer

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(models.Review, pk=review_id)
        instance = serializer.save(author=self.request.user, review=review)
        self.read_serializer_instance = (
            serializers.CommentReadSerializer(instance)
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        self.read_serializer_instance = (
            serializers.CommentReadSerializer(instance)
        )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return models.Comment.objects.filter(review_id=review_id)
