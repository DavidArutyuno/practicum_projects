from rest_framework import mixins, serializers, viewsets
from rest_framework.filters import SearchFilter

from api.permissions import IsAdminOrReadOnly


class UsernameValidationMixin:
    """Миксин для проверки username на запрещенные значения."""

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value


class EmailValidationMixin:
    """Миксин для проверки наличия email."""

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email - обязательное поле.")
        return value.lower()


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
