from annoying.fields import AutoOneToOneField
from django.contrib.auth import get_user_model
from django.db import models

from .const import (
    MAX_NAME_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_UNIT_LENGTH,
    MAX_URL_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Имя',
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Слаг',
    )

    def __str__(self) -> str:
        return f'#{self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MAX_UNIT_LENGTH,
        verbose_name='Единица измерения',
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин.)',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    favorited_by_users = models.ManyToManyField(
        User,
        related_name='favorited_recipes',
        blank=True,
        verbose_name='В списках избранного',
    )

    def __str__(self) -> str:
        return f'{self.name} - {self.author}'

    @property
    def favorite_count(self) -> int:
        return self.favorited_by_users.count()

    favorite_count.fget.short_description = 'Раз добавлен в избранное'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
    )

    def __str__(self) -> str:
        return f'[{self.recipe.name}] <-> [{self.ingredient.name}]'


class ShoppingCart(models.Model):
    user = AutoOneToOneField(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
    )

    def __str__(self) -> str:
        return f'Список покупок {self.user}'


class ShortLink(models.Model):
    full_url = models.URLField(
        max_length=MAX_URL_LENGTH,
        unique=True,
        verbose_name='Полная ссылка',
    )
    short_url = models.CharField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Короткий идентификатор',
    )

    def __str__(self) -> str:
        return f'{self.short_url} -> {self.full_url}'
