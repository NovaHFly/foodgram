from rest_framework.routers import DefaultRouter

from .views import UsersView

router = DefaultRouter()
router.register('users', UsersView)

urlpatterns = router.urls
