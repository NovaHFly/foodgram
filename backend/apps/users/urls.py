from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UsersView

router = SimpleRouter()
router.register('users', UsersView, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
