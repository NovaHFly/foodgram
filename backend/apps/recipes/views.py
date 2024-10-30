from typing import Callable

from django.db.models import Manager, Model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, ShortLink, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortLinkSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from .util import generate_shopping_list


class IngredientsView(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagsView(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipesView(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer: RecipeSerializer) -> None:
        serializer.save(author=self.request.user)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        return super().update(request, *args, **kwargs)

    def _add_to_list(
        self,
        request: Request,
        get_related_manager: Callable[[Model], Manager],
    ) -> Response:
        recipe = self.get_object()
        current_user = request.user

        related_manager = get_related_manager(current_user)

        if recipe in related_manager.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        related_manager.add(recipe)

        return Response(
            ShortRecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=HTTP_201_CREATED,
        )

    def _remove_from_list(
        self,
        request: Request,
        get_related_manager: Callable[[Model], Manager],
    ) -> Response:
        recipe = self.get_object()
        current_user = request.user

        related_manager = get_related_manager(current_user)

        if recipe not in related_manager.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        related_manager.remove(recipe)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request: Request, pk: int) -> Response:
        return self._add_to_list(request, lambda user: user.favorited_recipes)

    @favorite.mapping.delete
    def unfavorite(self, request: Request, pk: int) -> Response:
        return self._remove_from_list(
            request,
            lambda user: user.favorited_recipes,
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[AllowAny],
    )
    def get_link(self, request: Request, pk: int) -> Response:
        self.get_object()
        serializer = ShortLinkSerializer(
            data={'recipe_id': pk},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        recipes = request.user.shopping_cart.recipes.all()
        return HttpResponse(
            generate_shopping_list(recipes),
            content_type='text/plain; charset=UTF-8',
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def add_to_shopping_cart(self, request: Request, pk: int) -> Response:
        return self._add_to_list(
            request,
            lambda user: user.shopping_cart.recipes,
        )

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request: Request, pk: int) -> Response:
        return self._remove_from_list(
            request,
            lambda user: user.shopping_cart.recipes,
        )


@api_view(['get'])
@permission_classes([AllowAny])
def unshorten_link(request: Request, short_url: str) -> HttpResponse:
    full_url = get_object_or_404(ShortLink, short_url=short_url).full_url
    return HttpResponseRedirect(full_url)
