from rest_framework.routers import SimpleRouter

from .views import SubscriptionsView

router = SimpleRouter()
router.register(
    'users',
    SubscriptionsView,
    basename='users',
)

urlpatterns = router.urls
