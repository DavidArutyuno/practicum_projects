from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только автор объекта или администратор может изменять или
    удалять, остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated and (
                obj.author == user or user.is_staff or user.is_superuser
            )
        ) 