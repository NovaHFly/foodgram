from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(
        self,
        request: Request,
        _view: View,
        obj: Model,
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsStaffOrSuperuser(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return not request.user.is_anonymous and (
            request.user.is_staff or request.user.is_superuser
        )
