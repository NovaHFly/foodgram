from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Tag


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
    measurement_unit = serializers.CharField(source='unit')

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
        source='ingredient.unit',
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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)

    cooking_time = serializers.IntegerField(source='cook_time')
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'author',
            'cooking_time',
            'text',
        )

        read_only_fields = ('author',)

    def _write(self, validated_data, recipe=None):
        recipe_ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        if recipe is None:
            recipe = Recipe.objects.create(**validated_data)

        if recipe_ingredients:
            recipe.ingredients.all().delete()

        for recipe_ingredient in recipe_ingredients:
            ingredient_id = recipe_ingredient['ingredient']['id']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_id),
                amount=recipe_ingredient['amount'],
            )

        if tags:
            recipe.tags.set(Tag.objects.get(id=tag['id']) for tag in tags)

        return recipe

    def create(self, validated_data):
        return self._write(validated_data)

    def update(self, instance, validated_data):
        return self._write(validated_data, recipe=instance)