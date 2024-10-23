import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'author',
            'image',
            'cooking_time',
            'text',
        )

        read_only_fields = ('author',)

    def _write(self, validated_data, recipe=None):
        recipe_ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        image = validated_data.pop('image', None)

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
