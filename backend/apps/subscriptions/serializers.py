from rest_framework import serializers

from recipes.serializers import ShortRecipeSerializer
from users.models import FoodgramUser
from users.serializers import UserSerializer


class SubscriptionUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        fields += ('recipes', 'recipes_count')

    def get_recipes_count(self, user: FoodgramUser) -> int:
        return user.recipes.count()

    def get_recipes(self, user: FoodgramUser) -> list[dict]:
        request = self.context['request']
        recipes = user.recipes.all()

        data = ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data

        if (
            'recipes_limit' in request.query_params
            and request.query_params['recipes_limit'].isdigit()
        ):
            limit = int(request.query_params['recipes_limit'])
            data = data[:limit]

        return data