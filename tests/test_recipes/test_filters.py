from random import choice, choices, randint

from pytest import mark

from recipes.models import Tag

from .conftest import RANDOM_NAME_POOL

pytestmark = mark.depends(on=['endpoints_valid'])


@mark.usefixtures('create_many_ingredients')
def test_filter_ingredient_by_name(reader_client, ingredient_list_url):
    query = choice(RANDOM_NAME_POOL).lower()
    data = reader_client.get(ingredient_list_url + f'?name={query}').data
    assert all(query in ingredient['name'].lower() for ingredient in data)


@mark.usefixtures('create_many_recipes')
def test_filter_recipe_by_author(reader_client, recipe_list_url):
    query = reader_client.user.id
    data = reader_client.get(
        recipe_list_url + f'?author={query}',
    ).data['results']
    assert all(recipe['author']['id'] == query for recipe in data)


@mark.usefixtures('create_many_recipes')
def test_filter_recipe_by_tags(reader_client, recipe_list_url):
    random_tag_slugs = [
        tag.slug for tag in choices(Tag.objects.all(), k=randint(1, 3))
    ]
    query = '&'.join(f'tags={slug}' for slug in random_tag_slugs)
    data = reader_client.get(recipe_list_url + f'?{query}').data['results']
    assert all(
        any(tag['slug'] in random_tag_slugs for tag in recipe['tags'])
        for recipe in data
    )
