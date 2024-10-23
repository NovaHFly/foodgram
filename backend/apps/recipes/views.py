from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)


class IngredientsView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthorOrReadOnly]


class TagsView(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthorOrReadOnly]


class RecipesView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk: int):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if recipe in user.favorited_recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.favorited_recipes.add(recipe)
        return Response(
            RecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk: int):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if recipe not in user.favorited_recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.favorited_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
