from rest_framework.routers import DefaultRouter

from recipes.views import IngredientsView, RecipesView, TagsView
from users.views import AuthView, UserProfileView, UsersView

router = DefaultRouter()
router.register('recipes', RecipesView, basename='recipes')
router.register('ingredients', IngredientsView, basename='ingredients')
router.register('tags', TagsView, basename='tags')
router.register('auth/token', AuthView, basename='auth')
router.register('users', UserProfileView, basename='user_profile')
router.register('users', UsersView, basename='users')


urlpatterns = router.urls
