from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# TODO: Generalize image upload path
# TODO: Remove magic values
# TODO: Add verbose names


class Tag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=32,
    )
    unit = models.CharField(
        max_length=8,
    )


class Recipe(models.Model):
    name = models.CharField(
        max_length=64,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    cook_time = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    tags = models.ManyToManyField(Tag)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
    )
    ingredient = models.ForeignKey(Ingredient)
    amount = models.IntegerField()


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
