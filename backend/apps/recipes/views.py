from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, ShortLink, Tag
from .permissions import IsAuthorOrReadOnly, IsStaffOrSuperuser
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortLinkSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from .util import generate_shopping_cart

# TODO: Remove duplicate code


class IngredientsView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagsView(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = None


class RecipesView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthorOrReadOnly | IsStaffOrSuperuser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

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
            ShortRecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk: int):
        recipe = self.get_object()
        user = request.user

        if recipe not in user.favorited_recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.favorited_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk: int):
        self.get_object()
        serializer = ShortLinkSerializer(
            data={'recipe_id': pk},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        recipes = request.user.shopping_cart.recipes.all()
        return Response(
            generate_shopping_cart(recipes),
            content_type='text/plain charset=utf-8',
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
    )
    def add_to_shopping_cart(self, request, pk: int):
        recipe = self.get_object()
        current_user = request.user

        if recipe in current_user.shopping_cart.recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.add(recipe)
        return Response(
            ShortRecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk: int):
        recipe = self.get_object()
        current_user = request.user

        if recipe not in current_user.shopping_cart.recipes.all():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['get'])
@permission_classes([AllowAny])
def unshorten_link(request, short_url):
    full_url = get_object_or_404(ShortLink, short_url=short_url).full_url
    return HttpResponseRedirect(full_url)
