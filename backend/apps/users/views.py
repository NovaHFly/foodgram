from typing import Type

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet, ViewSet

from .models import FoodgramUser
from .serializers import (
    AuthSerializer,
    AvatarSerializer,
    CreateUserSerializer,
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
    permission_classes = [AllowAny]

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request):
        return Response(
            UserSerializer(
                request.user,
                context=self.get_serializer_context(),
            ).data
        )

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
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

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request: Request) -> Response:
        serializer = PasswordChangeSerializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthView(ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
    )
    def login(self, request: Request) -> Response:
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'auth_token': token.key})

    @action(
        detail=False,
        methods=['post'],
    )
    def logout(self, request: Request) -> Response:
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
