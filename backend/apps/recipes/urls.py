from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientsView,
    RecipesView,
    TagsView,
)

router = DefaultRouter()
router.register('recipes', RecipesView, basename='recipes')
router.register('ingredients', IngredientsView, basename='ingredients')
router.register('tags', TagsView, basename='tags')

urlpatterns = router.urls
