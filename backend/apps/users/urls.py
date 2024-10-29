from rest_framework.routers import SimpleRouter

from users.views import AuthView, UsersView

router = SimpleRouter()
router.register('auth/token', AuthView, basename='auth')
router.register('users', UsersView, basename='users')

urlpatterns = router.urls
