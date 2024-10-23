from rest_framework.routers import DefaultRouter

from .views import AuthView, UsersView

router = DefaultRouter()
router.register('users', UsersView, basename='users')
router.register('auth/token', AuthView, basename='auth')

urlpatterns = router.urls
