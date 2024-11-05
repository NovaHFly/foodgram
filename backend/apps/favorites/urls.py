from rest_framework.routers import SimpleRouter

from .views import FavoriteRecipesView

router = SimpleRouter()
router.register(
    'recipes',
    FavoriteRecipesView,
    basename='favorite_recipes',
)

urlpatterns = router.urls
