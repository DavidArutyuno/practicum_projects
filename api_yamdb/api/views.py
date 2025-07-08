from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from api import serializers
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
        - По полям 'name' и 'year'.
    """
    queryset = models.Title.objects.all()
    serializer_class = serializers.TitleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'year',]
