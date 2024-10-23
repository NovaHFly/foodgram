from rest_framework import serializers

from common.serializers import Base64ImageField
from common.util import generate_token

from .models import Ingredient, Recipe, RecipeIngredient, ShortLink, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('name', 'slug')

    def to_internal_value(self, data):
        return {'id': data}

    def validate(self, attrs):
        tag_id = attrs['id']
        if not isinstance(tag_id, int):
            raise serializers.ValidationError(f'{tag_id} is not an integer!')
        if not Tag.objects.filter(id=tag_id).exists():
            raise serializers.ValidationError(
                f'Tag with id {tag_id} does not exist!'
            )
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def validate_id(self, data):
        if not Ingredient.objects.filter(id=data).exists():
            raise serializers.ValidationError(
                f'Ingredient with id {data} does not exist!'
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_to_ingredient',
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'is_favorited',
            'name',
            'author',
            'image',
            'cooking_time',
            'text',
        )

        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        if request := self.context.get('request', None):
            current_user = request.user
            if current_user.is_anonymous:
                return False
            return obj in current_user.favorited_recipes.all()
        return False

    def _write(self, validated_data, recipe=None):
        recipe_ingredients = validated_data.pop('recipe_to_ingredient', [])
        tags = validated_data.pop('tags', [])
        image = validated_data.pop('image', None)

        if recipe is None:
            recipe = Recipe.objects.create(**validated_data)
        else:
            for key, value in validated_data.items():
                setattr(recipe, key, value)

        if recipe_ingredients:
            recipe.ingredients.clear()

        for recipe_ingredient in recipe_ingredients:
            ingredient = Ingredient.objects.get(
                id=recipe_ingredient['ingredient']['id']
            )
            recipe.ingredients.add(
                ingredient,
                through_defaults={'amount': recipe_ingredient['amount']},
            )

        if tags:
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


class ShortLinkSerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField()

    class Meta:
        model = ShortLink
        fields = ('id', 'recipe_id')

    def to_representation(self, instance):
        host_with_schema = (
            self.context['request'].get_raw_uri().partition('/api/')[0]
        )
        return {'short-link': f'{host_with_schema}/s/{instance.short_url}'}

    def create(self, validated_data):
        host_with_schema = (
            self.context['request'].get_raw_uri().partition('/api/')[0]
        )
        full_url = f'{host_with_schema}/recipes/{validated_data["recipe_id"]}/'
        while True:
            short_url = generate_token()
            if not ShortLink.objects.filter(short_url=short_url).exists():
                break

        short_link, _ = ShortLink.objects.get_or_create(
            full_url=full_url,
            short_url=short_url,
        )

        return short_link
