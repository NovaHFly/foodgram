from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import GenericViewSet

from recipes.models import Recipe
from recipes.serializers import ShortRecipeSerializer

from .util import generate_shopping_list


class ShoppingCartView(GenericViewSet):
    queryset = Recipe.objects.all()

    @action(
        detail=False,
        methods=['get'],
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
    )
    def shopping_cart(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        current_user = request.user

        if recipe in current_user.shopping_cart.recipes.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.add(recipe)

        return Response(
            ShortRecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=HTTP_201_CREATED,
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        current_user = request.user

        if recipe not in current_user.shopping_cart.recipes.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.shopping_cart.recipes.remove(recipe)
        return Response(status=HTTP_204_NO_CONTENT)
