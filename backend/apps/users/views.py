from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from .models import User
from .serializers import AuthSerializer, AvatarSerializer, UserSerializer


class UsersView(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'DELETE':
            return Response(['delete avatar'])
        return Response(['put avatar'])

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        return Response(['set passwrod'])


class AuthView(ViewSet):
    @action(detail=False, methods=['post'])
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
