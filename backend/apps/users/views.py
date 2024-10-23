from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
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
    permission_classes = [AllowAny]


class UserProfileView(GenericViewSet):
    @action(detail=False, methods=['get'])
    def me(self, request):
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
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
            context=self.get_serializer_context(),
        )
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


class SubscriptionView(GenericViewSet):
    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        return Response(
            UserSerializer(
                request.user.subscriptions.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )

    @action(detail=True, methods=['post'])
    def subscribe(self, request: Request, pk: int):
        user_to_subscribe = get_object_or_404(FoodgramUser, id=pk)
        current_user = request.user

        if current_user == user_to_subscribe:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user_to_subscribe in current_user.subscriptions.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.subscriptions.add(user_to_subscribe)

        return Response(
            UserSerializer(
                user_to_subscribe,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request: Request, pk: int):
        current_user = request.user
        user_to_unsubscribe = get_object_or_404(FoodgramUser, id=pk)

        if user_to_unsubscribe not in current_user.subscriptions.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.subscriptions.remove(user_to_unsubscribe)

        return Response(status=status.HTTP_204_NO_CONTENT)
