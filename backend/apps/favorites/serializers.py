from rest_framework.serializers import SerializerMethodField

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


def get_is_favorited(self, recipe: Recipe) -> bool:
    if not (request := self.context.get('request')):
        return False
    current_user = request.user
    if current_user.is_anonymous:
        return False
    return recipe in current_user.favorites_list.recipes.all()


RecipeSerializer._declared_fields['is_favorited'] = SerializerMethodField()
RecipeSerializer.Meta.fields += ['is_favorited']
RecipeSerializer.get_is_favorited = get_is_favorited
