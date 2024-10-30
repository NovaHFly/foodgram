from django.db.models import Model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import View


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Allow read only access for every user and full access to item author."""

    def has_object_permission(
        self,
        request: Request,
        _view: View,
        obj: Model,
    ) -> bool:
        return request.method in SAFE_METHODS or obj.author == request.user
