from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, Tag, User
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    TagSerializer,
)


class IngredientsView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagsView(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipesView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=User.objects.get(id=1))
        # serializer.save(author=self.request.user)
