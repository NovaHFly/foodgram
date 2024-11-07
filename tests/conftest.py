import shutil
import tempfile
from datetime import datetime, timedelta
from random import choice, choices, randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest import fixture
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, Tag

from .const import (
    NEW_PASSWORD,
    PASSWORD,
    RANDOM_NAME_POOL,
)
from .util import create_recipe, create_user, create_user_client

User = get_user_model()


@fixture(scope='session', autouse=True)
def setup_media_root():
    settings.MEDIA_ROOT = tempfile.mkdtemp()
    yield
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


@fixture
def small_gif() -> bytes:
    return (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )


@fixture
def gif_base64() -> str:
    return (
        'data:image/gif;base64,'
        'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    )


@fixture
def another_gif_base64() -> str:
    return (
        'data:image/gif;base64,'
        'R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
    )


@fixture
def some_image(small_gif) -> SimpleUploadedFile:
    return SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')


@fixture
def reader_user(some_image) -> AbstractUser:
    return create_user('reader', avatar=some_image)


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
def recipe(author_user, tag, ingredient, some_image) -> Recipe:
    return create_recipe(
        {
            'name': 'recipe',
            'author': author_user,
            'cooking_time': 1,
            'text': 'Lorem ipsum',
            'image': some_image,
        },
        [tag],
        [(ingredient, 1)],
    )


@fixture
def create_many_recipes(
    author_user,
    reader_user,
    some_image,
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
                'image': some_image,
                'pub_date': datetime.now() - timedelta(randint(0, 50)),
            },
            recipe_tags,
            ingredients_with_amounts,
        )


@fixture
def new_recipe_data(
    another_tag,
    another_ingredient,
    gif_base64,
) -> dict:
    return {
        'tags': [another_tag.id],
        'ingredients': [
            {'id': another_ingredient.id, 'amount': 15},
        ],
        'name': 'New recipe',
        'text': 'Some description',
        'cooking_time': 5,
        'image': gif_base64,
    }


@fixture
def new_user_data() -> dict[str, str]:
    return {
        'email': 'new_user@user.com',
        'username': 'new_user',
        'first_name': 'New',
        'last_name': 'user',
        'password': PASSWORD,
    }


@fixture
def change_password_data() -> dict[str, str]:
    return {
        'current_password': PASSWORD,
        'new_password': NEW_PASSWORD,
    }


@fixture
def new_avatar_data(another_gif_base64) -> dict[str, str]:
    return {'avatar': another_gif_base64}


@fixture
def reader_login_data(reader_user) -> dict[str, str]:
    return {
        'email': reader_user.email,
        'password': PASSWORD,
    }


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
def create_recipes_with_overlapping_ingredients(
    tag,
    author_user,
    some_image,
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
                'image': some_image,
            },
            [tag],
            ingredients_with_amounts,
        )


@fixture
def add_all_recipes_to_reader_shopping_cart(reader_user):
    for recipe in Recipe.objects.all():
        reader_user.shopping_cart.recipes.add(recipe)


@fixture
def subscription_user_schema(user_schema, short_recipe_schema) -> dict:
    schema = user_schema.copy()
    schema['properties'] |= {
        'recipes': {
            'type': 'array',
            'items': short_recipe_schema,
        },
        'recipes_count': {'type': 'number'},
    }
    return schema


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
def subscribe_to_reader_url(reader_user) -> str:
    return reverse('users-subscribe', kwargs={'pk': reader_user.id})


@fixture
def subscribe_to_author_url(author_user) -> str:
    return reverse('users-subscribe', kwargs={'pk': author_user.id})


@fixture
def nonexistant_user_subscribe_url() -> str:
    return reverse('users-subscribe', kwargs={'pk': 1000})


@fixture
def tag_schema() -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'slug': {'type': 'string'},
        },
    }


@fixture
def ingredient_schema() -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'measurement_unit': {'type': 'string'},
        },
    }


@fixture
def recipe_schema(
    tag_schema,
    ingredient_schema,
    user_schema,
) -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'tags': {
                'type': 'array',
                'items': tag_schema,
            },
            'ingredients': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': ingredient_schema['properties']
                    | {'amount': {'type': 'number'}},
                },
            },
            'author': user_schema,
            'name': {'type': 'string'},
            'image': {'type': 'string'},
            'text': {'type': 'string'},
            'cooking_time': {'type': 'number'},
        },
    }


@fixture
def user_schema() -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'email': {'type': 'string'},
            'username': {'type': 'string'},
            'first_name': {'type': 'string'},
            'last_name': {'type': 'string'},
            'avatar': {'type': ['string', 'null']},
        },
    }


@fixture
def user_register_confirmation_schema() -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'email': {'type': 'string'},
            'username': {'type': 'string'},
            'first_name': {'type': 'string'},
            'last_name': {'type': 'string'},
        },
    }


@fixture
def short_recipe_schema() -> dict:
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'image': {'type': 'string'},
            'cooking_time': {'type': 'number'},
        },
    }
