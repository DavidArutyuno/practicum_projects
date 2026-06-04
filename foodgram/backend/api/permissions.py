from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает доступ:
    - всем пользователям на безопасные методы (GET, HEAD, OPTIONS)
    - только автору объекта на остальные методы

    Пример использования:
        permission_classes = [IsAuthorOrReadOnly]
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                obj.author == request.user
            )
        )
