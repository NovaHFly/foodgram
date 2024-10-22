from rest_framework.routers import DefaultRouter

from .views import AuthView, SubscriptionView, UserProfileView, UsersView

router = DefaultRouter()
router.register('users', SubscriptionView, basename='subscriptions')
router.register('users', UserProfileView, basename='user_profile')
router.register('users', UsersView, basename='users')
router.register('auth/token', AuthView, basename='auth')

urlpatterns = router.urls
