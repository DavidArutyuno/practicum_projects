"""Вспомогательные классы-миксины."""

from rest_framework import mixins, viewsets


class CreateListViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Реализация только GET и POST запросов."""
    pass
