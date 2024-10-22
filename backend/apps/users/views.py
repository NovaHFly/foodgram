from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from .models import FoodgramUser
from .serializers import (
    AuthSerializer,
    AvatarSerializer,
    PasswordChangeSerializer,
    UserSerializer,
)


class UsersView(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = FoodgramUser.objects.all()
    serializer_class = UserSerializer


class UserProfileView(ViewSet):
    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
    )
    def avatar(self, request):
        serializer = AvatarSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthView(ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'auth_token': token.key})

    @action(detail=False, methods=['post'])
    def logout(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
