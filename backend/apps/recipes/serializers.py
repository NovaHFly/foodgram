from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


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


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )
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

    def validate_ingredients(self, recipe_inredients):
        for recipe_ingredient in recipe_inredients:
            ing_id = recipe_ingredient['ingredient']['id']
            if not Ingredient.objects.filter(id=ing_id).exists():
                raise serializers.ValidationError(
                    f'Ingredient with id {ing_id} does not exist!'
                )

        return recipe_inredients

    def validate_tags(self, tags):
        for tag_id in tags:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'Tag with id {tag_id} does not exist!'
                )

        return tags

    def _write(self, validated_data, recipe=None):
        recipe_ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        if recipe is None:
            recipe = Recipe.objects.create(**validated_data)
        else:
            recipe.ingredients.all().delete()

        for recipe_ingredient in recipe_ingredients:
            ingredient_id = recipe_ingredient['ingredient']['id']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_id),
                amount=recipe_ingredient['amount'],
            )

        recipe.tags.set(Tag.objects.get(id=tag_id) for tag_id in tags)

        return recipe

    def create(self, validated_data):
        return self._write(validated_data)

    def update(self, instance, validated_data):
        return self._write(validated_data, recipe=instance)


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, read_only=True)
