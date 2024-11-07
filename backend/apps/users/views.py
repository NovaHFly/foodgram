from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import FoodgramUser
from .serializers import AvatarSerializer


class UsersView(UserViewSet):
    queryset = FoodgramUser.objects.all()

    def get_permissions(self):
        if self.action in ('me', 'avatar', 'delete_avatar'):
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
    )
    def avatar(self, request: Request) -> Response:
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request: Request) -> Response:
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
