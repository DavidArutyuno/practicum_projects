from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from api.permissions import IsAdminOrReadOnly


class BaseViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    permission_classes = (IsAdminOrReadOnly,)
