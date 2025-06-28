from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsAuthorOrReadOnly(BasePermission):
    """
    Проверка прав.

    Разрешения на уровне запроса:
        только аутентифицированные пользователи или
        безопасные методы.

    Разрешения на уровне объекта:
        разрешены изменения, если запрос пришел от автора объекта.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
