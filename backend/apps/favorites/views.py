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


class FavoriteRecipesView(GenericViewSet):
    queryset = Recipe.objects.all()

    @action(detail=True, methods=['post'])
    def favorite(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        current_user = request.user

        if recipe in current_user.favorites_list.recipes.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.favorites_list.recipes.add(recipe)

        return Response(
            ShortRecipeSerializer(
                recipe,
                context=self.get_serializer_context(),
            ).data,
            status=HTTP_201_CREATED,
        )

    @favorite.mapping.delete
    def unfavorite(self, request: Request, pk: int) -> Response:
        recipe = self.get_object()
        current_user = request.user

        if recipe not in current_user.favorites_list.recipes.all():
            return Response(status=HTTP_400_BAD_REQUEST)

        current_user.favorites_list.recipes.remove(recipe)
        return Response(status=HTTP_204_NO_CONTENT)
