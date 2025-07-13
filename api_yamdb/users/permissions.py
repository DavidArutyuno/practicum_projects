from rest_framework.permissions import BasePermission, SAFE_METHODS


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
    """Разрешает полный доступ администраторам и только чтение остальным.

    Разрешает:
    - GET, HEAD, OPTIONS запросы всем пользователям
    - POST, PUT, PATCH, DELETE только администраторам (is_admin=True)

    Attributes:
        SAFE_METHODS: Кортеж ('GET', 'HEAD', 'OPTIONS')

    Пример использования:
        permission_classes = [IsAdminOrReadOnly]
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsOwnerAdminModeratorOrReadOnly(BasePermission):
    """Разрешает доступ владельцу, администратору, модератору или
    только чтение.

    Проверяет разрешения на уровне объекта:
    - Чтение разрешено всем
    - Изменение разрешено:
        * Автору объекта (obj.author)
        * Пользователям с is_admin=True
        * Пользователям с is_moderator=True

    Args:
        request: Объект запроса
        view: ViewSet или APIView
        obj: Проверяемый объект модели

    Returns:
        bool: True если доступ разрешен, иначе False

    Пример использования:
        permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.is_admin
                         or request.user.is_moderator
                         or obj.author == request.user)))
