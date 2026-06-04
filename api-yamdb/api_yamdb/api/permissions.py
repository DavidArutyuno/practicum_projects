from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Разрешает доступ:
    - всем пользователям на безопасные методы (GET, HEAD, OPTIONS)
    - только аутентифицированным пользователям на остальные методы

    Пример использования:
        permission_classes = [IsAuthenticatedOrReadOnly]
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAdmin(BasePermission):
    """Проверяет, является ли пользователь администратором или
    суперпользователем.

    Разрешает доступ только аутентифицированным пользователям с флагом
    is_admin=True или суперпользователям (is_superuser=True).

    Пример использования:
        permission_classes = [IsAdmin]
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser))


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ:
    - всем пользователям на безопасные методы (GET, HEAD, OPTIONS)
    - только аутентифицированным администраторам (is_admin=True)
      или суперпользователям на остальные методы

    Атрибуты:
        SAFE_METHODS: кортеж методов ('GET', 'HEAD', 'OPTIONS')

    Пример использования:
        permission_classes = [IsAdminOrReadOnly]
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """
    Разрешает доступ к объекту:
    - всем пользователям на безопасные методы
    - только автору объекта, модераторам или администраторам
      на изменяющие методы (POST, PUT, PATCH, DELETE)

    Параметры:
        request: HttpRequest объект
        view: ViewSet или APIView
        obj: объект модели, к которому проверяется доступ

    Возвращает:
        bool: True если доступ разрешен, иначе False

    Пример использования:
        permission_classes = [IsAuthorOrModeratorOrAdmin]
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
