from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Ingredient, Recipe, ShortLink, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortLinkSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)

# TODO: Remove duplicate code


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
        recipe = self.get_object()
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
        recipe = self.get_object()
        user = request.user

        if recipe not in user.favorited_recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.favorited_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk: int):
        self.get_object()
        serializer = ShortLinkSerializer(
            data={'recipe_id': pk},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk: int):
        recipe = self.get_object()
        current_user = request.user

        if recipe in current_user.shopping_cart.recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.add(recipe)
        return Response(
            ShortRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk: int):
        recipe = self.get_object()
        current_user = request.user

        if recipe not in current_user.shopping_cart.recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['get'])
def unshorten_link(request, short_url):
    full_url = get_object_or_404(ShortLink, short_url=short_url).full_url
    return HttpResponseRedirect(full_url)
