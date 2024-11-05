from rest_framework.serializers import SerializerMethodField

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
    if not (request := self.context.get('request')):
        return False
    current_user = request.user
    if current_user.is_anonymous:
        return False
    return recipe in current_user.shopping_cart.recipes.all()


RecipeSerializer._declared_fields['is_in_shopping_cart'] = (
    SerializerMethodField()
)
RecipeSerializer.Meta.fields += ['is_in_shopping_cart']
RecipeSerializer.get_is_in_shopping_cart = get_is_in_shopping_cart
