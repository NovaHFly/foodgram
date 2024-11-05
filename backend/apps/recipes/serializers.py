from typing import Callable

from django.db.models import Manager, Model
from rest_framework import serializers

from common.serializers import Base64ImageField
from users import serializers as users_serializers
from users.models import FoodgramUser

from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .util import contains_duplicates


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['name', 'slug']

    def to_internal_value(self, data: int) -> dict[str, int]:
        return {'id': data}

    def validate(self, attrs: dict[str, int]) -> dict[str, int]:
        tag_id = attrs['id']
        if not isinstance(tag_id, int):
            raise serializers.ValidationError(f'{tag_id} is not an integer!')
        if not Tag.objects.filter(id=tag_id).exists():
            raise serializers.ValidationError(
                f'Тег с id {tag_id} не существует!'
            )
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'name', 'measurement_unit']

    def validate_id(self, value: int) -> int:
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'Ингредиент с id {value} не существует!'
            )
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        many=True,
        allow_empty=False,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        allow_empty=False,
        source='recipe_to_ingredient',
    )
    image = Base64ImageField(required=False)
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = users_serializers.UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'ingredients',
            'is_in_shopping_cart',
            'name',
            'author',
            'image',
            'cooking_time',
            'text',
        ]

    def validate_ingredients(self, value: list[dict]) -> list[dict]:
        if contains_duplicates(value, lambda x: x['ingredient']['id']):
            raise serializers.ValidationError(
                'Нельзя добавить 2 одинаковых ингредиента!'
            )
        return value

    def validate_tags(self, value: list[dict]) -> list[dict]:
        if contains_duplicates(value, lambda x: x['id']):
            raise serializers.ValidationError(
                'Нельзя присвоить 2 одинаковых тега!'
            )
        return value

    def validate(self, attrs: dict) -> dict:
        if not self.instance:
            if 'image' not in attrs:
                raise serializers.ValidationError(
                    'Не загружена картинка рецепта!'
                )
        return attrs

    def _check_instance_in_user_list(
        self,
        recipe: Recipe,
        get_related_manager: Callable[[Model], Manager],
    ) -> bool:
        if not (request := self.context.get('request', None)):
            return False
        current_user: FoodgramUser = request.user
        if current_user.is_anonymous:
            return False
        related_manager = get_related_manager(current_user)
        return recipe in related_manager.all()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        return self._check_instance_in_user_list(
            recipe,
            lambda user: user.shopping_cart.recipes,
        )

    def _write(self, validated_data: dict, recipe: Recipe = None) -> Recipe:
        recipe_ingredients = validated_data.pop('recipe_to_ingredient', [])
        tags = validated_data.pop('tags', [])
        image = validated_data.pop('image', None)

        if recipe is None:
            recipe = Recipe.objects.create(**validated_data)
        else:
            for key, value in validated_data.items():
                setattr(recipe, key, value)

        recipe.ingredients.clear()

        for recipe_ingredient in recipe_ingredients:
            ingredient = Ingredient.objects.get(
                id=recipe_ingredient['ingredient']['id']
            )
            recipe.ingredients.add(
                ingredient,
                through_defaults={'amount': recipe_ingredient['amount']},
            )

        recipe.tags.set(Tag.objects.get(id=tag['id']) for tag in tags)

        if image:
            if recipe.image:
                recipe.image.delete()
            recipe.image = image

        recipe.save()
        return recipe

    def create(self, validated_data):
        return self._write(validated_data)

    def update(self, instance, validated_data):
        return self._write(validated_data, recipe=instance)
