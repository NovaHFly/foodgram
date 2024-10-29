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
    SubscriptionUserSerializer,
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

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request: Request) -> Response:
        paginated_data = self.paginate_queryset(
            SubscriptionUserSerializer(
                request.user.subscriptions.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )
        return self.get_paginated_response(paginated_data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request: Request, pk: int) -> Response:
        user_to_subscribe = self.get_object()
        current_user = request.user

        if current_user == user_to_subscribe:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user_to_subscribe in current_user.subscriptions.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.subscriptions.add(user_to_subscribe)

        return Response(
            SubscriptionUserSerializer(
                user_to_subscribe,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request: Request, pk: int) -> Response:
        current_user = request.user
        user_to_unsubscribe = self.get_object()

        if user_to_unsubscribe not in current_user.subscriptions.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.subscriptions.remove(user_to_unsubscribe)

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
