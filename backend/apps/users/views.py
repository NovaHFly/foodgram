from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserSerializer


class UsersView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    http_method_names = ['get', 'post', 'options']
