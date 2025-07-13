from rest_framework.permissions import (
    BasePermission, SAFE_METHODS
)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_superuser)
        )


class IsAuthorOrModeratorOrAdmin(BasePermission):
    # def has_permission(self, request, view):
    #     return (
    #         # request.method in SAFE_METHODS or
    #         request.user.is_user
    #     )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return (
            obj.author == request.user or
            request.user.is_moderator or
            request.user.is_admin
        )
