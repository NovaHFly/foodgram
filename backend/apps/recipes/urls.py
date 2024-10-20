from django.urls import include
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import IngredientsView, RecipesView, TagsView

router = DefaultRouter()
router.register('tags', TagsView)
router.register('ingredients', IngredientsView)
router.register('recipes', RecipesView)

urlpatterns = router.urls
