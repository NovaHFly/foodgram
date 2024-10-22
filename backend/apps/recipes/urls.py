from rest_framework.routers import DefaultRouter

from .views import IngredientsView, RecipesView, TagsView

router = DefaultRouter()
router.register('tags', TagsView)
router.register('ingredients', IngredientsView)
router.register('recipes', RecipesView)

urlpatterns = router.urls
