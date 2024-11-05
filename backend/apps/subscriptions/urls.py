from rest_framework.routers import SimpleRouter

from .views import SubscriptionsView

router = SimpleRouter()
router.register(
    'users',
    SubscriptionsView,
    basename='subscriptions',
)

urlpatterns = router.urls
