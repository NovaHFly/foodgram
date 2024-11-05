from rest_framework.routers import SimpleRouter

from .views import ShoppingCartView

router = SimpleRouter()
router.register('recipes', ShoppingCartView, basename='shopping_cart')

urlpatterns = router.urls
