from annoying.fields import AutoOneToOneField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# TODO: Generalize image upload path
# TODO: Remove magic values
# TODO: Add verbose names


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=32, unique=True)

    def __str__(self) -> str:
        return f'#{self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=16,
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=64,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    cooking_time = models.IntegerField()
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    favorited_by_users = models.ManyToManyField(
        User, related_name='favorited_recipes', blank=True,
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.author}'

    @property
    def favorite_count(self) -> int:
        return self.favorited_by_users.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe',
    )
    amount = models.IntegerField()

    def __str__(self) -> str:
        return f'[{self.recipe.name}] <-> [{self.ingredient.name}]'


class ShoppingCart(models.Model):
    user = AutoOneToOneField(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(Recipe)

    def __str__(self) -> str:
        return f'Список покупок {self.user}'


class ShortLink(models.Model):
    full_url = models.URLField(max_length=200, unique=True)
    short_url = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return f'{self.short_url} -> {self.full_url}'
