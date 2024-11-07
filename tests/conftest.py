import shutil
import tempfile
from datetime import datetime, timedelta
from random import choice, choices, randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from pytest import fixture
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, Tag

from .const import GIF_BASE64, RANDOM_NAME_POOL, SOME_IMAGE
from .util import create_recipe, create_user, create_user_client

User = get_user_model()


@fixture(scope='session', autouse=True)
def setup_media_root():
    settings.MEDIA_ROOT = tempfile.mkdtemp()
    yield
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


@fixture
def reader_user() -> AbstractUser:
    return create_user('reader', avatar=SOME_IMAGE)


@fixture
def author_user() -> AbstractUser:
    return create_user('author')


@fixture
def anon_client() -> APIClient:
    return APIClient()


@fixture
def reader_client(reader_user) -> APIClient:
    return create_user_client(reader_user)


@fixture
def author_client(author_user) -> APIClient:
    return create_user_client(author_user)


@fixture
def tag() -> Tag:
    return Tag.objects.create(
        name='Some tag',
        slug='some_tag',
    )


@fixture
def another_tag() -> Tag:
    return Tag.objects.create(
        name='Another tag',
        slug='another_tag',
    )


@fixture
def create_many_tags() -> None:
    tags = (
        Tag(
            name=f'{choice(RANDOM_NAME_POOL)}_{i}',
            slug=f'{choice(RANDOM_NAME_POOL)}_{i}',
        )
        for i in range(15)
    )
    Tag.objects.bulk_create(tags)


@fixture
def ingredient() -> Ingredient:
    return Ingredient.objects.create(
        name='Some ingredient',
        measurement_unit='g',
    )


@fixture
def another_ingredient() -> Ingredient:
    return Ingredient.objects.create(
        name='Another ingredient',
        measurement_unit='ml',
    )


@fixture
def create_many_ingredients() -> None:
    ingredients = (
        Ingredient(
            name=f'{choice(RANDOM_NAME_POOL)}_{i}',
            measurement_unit=f'{choice(RANDOM_NAME_POOL)}_{randint(1, 50)}',
        )
        for i in range(15)
    )
    Ingredient.objects.bulk_create(ingredients)


@fixture
def recipe(author_user, tag, ingredient) -> Recipe:
    return create_recipe(
        {
            'name': 'recipe',
            'author': author_user,
            'cooking_time': 1,
            'text': 'Lorem ipsum',
            'image': SOME_IMAGE,
        },
        [tag],
        [(ingredient, 1)],
    )


@fixture
def new_recipe_data(
    another_tag,
    another_ingredient,
) -> dict:
    return {
        'tags': [another_tag.id],
        'ingredients': [
            {'id': another_ingredient.id, 'amount': 15},
        ],
        'name': 'New recipe',
        'text': 'Some description',
        'cooking_time': 5,
        'image': GIF_BASE64,
    }


@fixture
def create_many_recipes(
    author_user,
    reader_user,
    create_many_tags,
    create_many_ingredients,
) -> None:
    tags = Tag.objects.all()
    ingredients = Ingredient.objects.all()

    for _ in range(15):
        recipe_tags = set(choices(tags, k=randint(1, 5)))
        recipe_ingredients = set(choices(ingredients, k=randint(1, 5)))
        ingredient_amounts = (50 for _ in range(len(recipe_ingredients)))
        ingredients_with_amounts = zip(recipe_ingredients, ingredient_amounts)
        create_recipe(
            {
                'name': f'{choice(RANDOM_NAME_POOL)}_{randint(1, 50)}',
                'author': choice([author_user, reader_user]),
                'cooking_time': randint(1, 50),
                'text': 'Lorem ipsum',
                'image': SOME_IMAGE,
                'pub_date': datetime.now() - timedelta(randint(0, 50)),
            },
            recipe_tags,
            ingredients_with_amounts,
        )


@fixture
def create_recipes_with_overlapping_ingredients(
    tag,
    author_user,
    create_many_ingredients,
):
    ingredients = Ingredient.objects.all()[:5]

    for _ in range(15):
        recipe_ingredients = set(choices(ingredients, k=randint(1, 3)))
        ingredient_amounts = (50 for _ in range(len(recipe_ingredients)))
        ingredients_with_amounts = zip(recipe_ingredients, ingredient_amounts)
        create_recipe(
            {
                'name': f'{choice(RANDOM_NAME_POOL)}_{randint(1, 50)}',
                'author': author_user,
                'cooking_time': 1,
                'text': 'Lorem ipsum',
                'image': SOME_IMAGE,
            },
            [tag],
            ingredients_with_amounts,
        )


@fixture
def subscribe_reader_to_author(
    reader_user,
    author_user,
):
    reader_user.subscription_list.users.add(author_user)


@fixture
def add_many_subscriptions(reader_user):
    for i in range(15):
        user = create_user(f'user {i}')
        reader_user.subscription_list.users.add(user)


@fixture
def add_recipe_to_reader_favorites(reader_user, recipe):
    reader_user.favorites_list.recipes.add(recipe)


@fixture
def add_random_recipes_to_reader_favorites(reader_user, create_many_recipes):
    recipes = set(choices(Recipe.objects.all(), k=7))
    for recipe in recipes:
        reader_user.favorites_list.recipes.add(recipe)


@fixture
def add_recipe_to_reader_shopping_cart(reader_user, recipe):
    reader_user.shopping_cart.recipes.add(recipe)


@fixture
def add_random_recipes_to_reader_shopping_cart(
    reader_user,
    create_many_recipes,
):
    recipes = set(choices(Recipe.objects.all(), k=7))
    for recipe in recipes:
        reader_user.shopping_cart.recipes.add(recipe)


@fixture
def add_all_recipes_to_reader_shopping_cart(reader_user):
    for recipe in Recipe.objects.all():
        reader_user.shopping_cart.recipes.add(recipe)


@fixture
def tag_list_url() -> str:
    return reverse('tags-list')


@fixture
def tag_detail_url(tag) -> str:
    return reverse('tags-detail', kwargs={'pk': tag.id})


@fixture
def nonexistant_tag_url() -> str:
    return reverse('tags-detail', kwargs={'pk': 1000})


@fixture
def ingredient_list_url() -> str:
    return reverse('ingredients-list')


@fixture
def ingredient_detail_url(ingredient) -> str:
    return reverse('ingredients-detail', kwargs={'pk': ingredient.id})


@fixture
def nonexistant_ingredient_url() -> str:
    return reverse('ingredients-detail', kwargs={'pk': 1000})


@fixture
def recipe_list_url() -> str:
    return reverse('recipes-list')


@fixture
def recipe_detail_url(recipe) -> str:
    return reverse('recipes-detail', kwargs={'pk': recipe.id})


@fixture
def nonexistant_recipe_url() -> str:
    return reverse('recipes-detail', kwargs={'pk': 1000})


@fixture
def recipe_favorite_url(recipe) -> str:
    return reverse('recipes-favorite', kwargs={'pk': recipe.id})


@fixture
def nonexistant_recipe_favorite_url() -> str:
    return reverse('recipes-favorite', kwargs={'pk': 1000})


@fixture
def recipe_shopping_cart_url(recipe) -> str:
    return reverse('recipes-shopping-cart', kwargs={'pk': recipe.id})


@fixture
def nonexistant_recipe_shopping_cart_url() -> str:
    return reverse('recipes-shopping-cart', kwargs={'pk': 1000})


@fixture
def recipe_get_link_url(recipe) -> str:
    return reverse('recipes-get-link', kwargs={'pk': recipe.id})


@fixture
def nonexistant_recipe_short_link_url() -> str:
    return reverse('recipes-get-link', kwargs={'pk': 1000})


@fixture
def download_shopping_cart_url() -> str:
    return reverse('recipes-download-shopping-cart')


@fixture
def users_list_url() -> str:
    return reverse('users-list')


@fixture
def author_user_url(author_user) -> str:
    return reverse('users-detail', kwargs={'id': author_user.id})


@fixture
def current_user_url() -> str:
    return reverse('users-me')


@fixture
def avatar_url() -> str:
    return reverse('users-avatar')


@fixture
def subscription_list_url() -> str:
    return reverse('users-subscriptions')


@fixture
def reader_subscribe_url(reader_user) -> str:
    return reverse('users-subscribe', kwargs={'pk': reader_user.id})


@fixture
def author_subscribe_url(author_user) -> str:
    return reverse('users-subscribe', kwargs={'pk': author_user.id})


@fixture
def nonexistant_user_subscribe_url() -> str:
    return reverse('users-subscribe', kwargs={'pk': 1000})
