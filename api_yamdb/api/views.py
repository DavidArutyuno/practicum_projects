from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status

from api import serializers
from api.filter import TitleFilter
from reviews import models


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title.

    CRUD-операции:
        - GET: Получение списка произведений или по id.
        - POST: Создание нового произведения.
        - PUT: Обновление информации о произведении.
        - PATCH: Частичное обновление информации о произведении.
        - DELETE: Удаление произведения.

    Фильтрация:
        - По полям 'name', 'year', 'category__slug'.
    """
    queryset = models.Title.objects.select_related('category')
    serializer_class = serializers.TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def perform_create(self, serializer):
        slug = self.request.data.get('category')
        category = get_object_or_404(models.Category, slug=slug)
        serializer.save(category=category)


class CategoryViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
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
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
