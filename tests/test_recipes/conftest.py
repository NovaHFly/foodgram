from datetime import datetime, timedelta
from random import choice, randint

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest import fixture

from recipes.models import Ingredient, Recipe, Tag

RANDOM_NAME_POOL = (
    'test',
    'another',
    'hello',
    'cat',
    'many',
    'job',
    'dog',
    'carrot',
)


@fixture
def tag() -> Tag:
    return Tag.objects.create(
        name='Some tag',
        slug='some_tag',
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
def another_tag() -> Tag:
    return Tag.objects.create(
        name='Another tag',
        slug='another_tag',
    )


@fixture
def ingredient() -> Ingredient:
    return Ingredient.objects.create(
        name='Some ingredient',
        measurement_unit='g',
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
def another_ingredient() -> Ingredient:
    return Ingredient.objects.create(
        name='Another ingredient',
        measurement_unit='ml',
    )


@fixture
def recipe_image(small_gif) -> SimpleUploadedFile:
    return SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')


@fixture
def recipe(author_user, tag, ingredient, recipe_image) -> Recipe:
    recipe = Recipe.objects.create(
        name='recipe',
        author=author_user,
        cooking_time=1,
        text='Lorem ipsum',
        image=recipe_image,
    )
    recipe.tags.add(tag)
    recipe.ingredients.add(ingredient, through_defaults={'amount': 1})
    recipe.save()

    return recipe


@fixture
def create_many_recipes(
    author_user,
    reader_user,
    recipe_image,
    create_many_tags,
    create_many_ingredients,
) -> None:
    tags = Tag.objects.all()
    ingredients = Ingredient.objects.all()
    for _ in range(15):
        recipe = Recipe.objects.create(
            name=f'{choice(RANDOM_NAME_POOL)}_{randint(1, 50)}',
            author=choice([author_user, reader_user]),
            cooking_time=randint(1, 50),
            text='Lorem ipsum',
            image=recipe_image,
            pub_date=datetime.now() - timedelta(randint(0, 50)),
        )
        for _ in range(randint(1, 5)):
            recipe.tags.add(choice(tags))
        for _ in range(randint(1, 5)):
            recipe.ingredients.add(
                choice(ingredients),
                through_defaults={
                    'amount': randint(1, 50),
                },
            )
        recipe.save()


@fixture
def tag_list_url() -> str:
    return reverse('tags-list')


@fixture
def tag_detail_url(tag) -> str:
    return reverse('tags-detail', kwargs={'pk': tag.id})


@fixture
def ingredient_list_url() -> str:
    return reverse('ingredients-list')


@fixture
def ingredient_detail_url(ingredient) -> str:
    return reverse('ingredients-detail', kwargs={'pk': ingredient.id})


@fixture
def recipe_list_url() -> str:
    return reverse('recipes-list')


@fixture
def recipe_detail_url(recipe) -> str:
    return reverse('recipes-detail', kwargs={'pk': recipe.id})


@fixture
def recipe_get_link_url(recipe) -> str:
    return reverse('recipes-get-link', kwargs={'pk': recipe.id})


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
