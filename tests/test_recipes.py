from random import choice, choices, randint

import jsonschema
from django.conf import settings
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from recipes.models import Recipe, Tag

from .conftest import RANDOM_NAME_POOL
from .util import (
    check_different_pages,
    check_recipe_is_the_same,
    check_recipe_updated,
    check_response_is_paginated,
)


@mark.parametrize(
    ('client', 'url'),
    (
        (lf('anon_client'), lf('tag_list_url')),
        (lf('anon_client'), lf('tag_detail_url')),
        (lf('anon_client'), lf('ingredient_list_url')),
        (lf('anon_client'), lf('ingredient_detail_url')),
        (lf('anon_client'), lf('recipe_list_url')),
        (lf('anon_client'), lf('recipe_detail_url')),
        (lf('anon_client'), lf('recipe_get_link_url')),
        (lf('reader_client'), lf('tag_list_url')),
        (lf('reader_client'), lf('tag_detail_url')),
        (lf('reader_client'), lf('ingredient_list_url')),
        (lf('reader_client'), lf('ingredient_detail_url')),
        (lf('reader_client'), lf('recipe_list_url')),
        (lf('reader_client'), lf('recipe_detail_url')),
        (lf('reader_client'), lf('recipe_get_link_url')),
    ),
)
def test_recipes_endpoints_available(client, url):
    assert client.get(url).status_code == HTTP_200_OK


@mark.parametrize(
    ('client', 'url', 'schema'),
    [
        (
            lf('reader_client'),
            lf('tag_detail_url'),
            lf('tag_schema'),
        ),
        (
            lf('reader_client'),
            lf('ingredient_detail_url'),
            lf('ingredient_schema'),
        ),
        (
            lf('reader_client'),
            lf('recipe_detail_url'),
            lf('recipe_schema'),
        ),
    ],
)
def test_recipes_response_schema(client, url, schema):
    jsonschema.validate(client.get(url).data, schema)


def test_recipe_list_is_paginated(
    reader_client,
    recipe_list_url,
):
    check_response_is_paginated(response=reader_client.get(recipe_list_url))


@mark.usefixtures('create_many_recipes')
def test_recipe_list_different_pages(reader_client, recipe_list_url):
    check_different_pages(reader_client, recipe_list_url)


@mark.usefixtures('create_many_recipes')
@mark.parametrize(
    ('query', 'length'),
    (
        ('', settings.REST_FRAMEWORK['PAGE_SIZE']),
        ('?limit=5', 5),
        ('?limit=1', 1),
        ('?limit=15', 15),
    ),
)
def test_recipe_list_page_size(
    reader_client,
    recipe_list_url,
    query,
    length,
):
    assert (
        len(reader_client.get(recipe_list_url + query).data['results'])
        == length
    )


@mark.usefixtures('create_many_recipes')
def test_recipe_ordering(reader_client, recipe_list_url):
    data = reader_client.get(recipe_list_url + '?limit=50').data['results']
    pub_dates = [
        Recipe.objects.get(id=recipe['id']).pub_date for recipe in data
    ]
    assert sorted(pub_dates, reverse=True) == pub_dates


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


def test_authorized_user_can_create_recipes(
    author_client,
    recipe_list_url,
    new_recipe_data,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_201_CREATED
    response_data = response.data
    assert (
        Recipe.objects.count()
        and Recipe.objects.filter(id=response_data['id']).exists()
    )

    recipe = Recipe.objects.get(id=response_data['id'])
    assert recipe.image is not None
    check_recipe_updated(
        recipe,
        new_recipe_data | {'author': author_client.user},
    )


def test_anon_cannot_create_recipes(
    anon_client,
    recipe_list_url,
    new_recipe_data,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    response = anon_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Recipe.objects.count()


def test_author_can_edit_their_recipes(
    author_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
):
    response = author_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_200_OK

    new_recipe = Recipe.objects.get(id=recipe.id)
    assert new_recipe.image != recipe.image
    check_recipe_updated(
        new_recipe,
        new_recipe_data | {'author': recipe.author},
    )


def test_user_cannot_edit_others_recipes(
    reader_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
):
    response = reader_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    new_recipe = Recipe.objects.get(id=recipe.id)
    check_recipe_is_the_same(new_recipe, recipe)


def test_author_can_delete_their_recipes(
    author_client,
    recipe,
    recipe_detail_url,
):
    recipe_id = recipe.id
    response = author_client.delete(recipe_detail_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Recipe.objects.filter(id=recipe_id).exists()


def test_user_cannot_delete_others_recipes(
    reader_client,
    recipe,
    recipe_detail_url,
):
    recipe_id = recipe.id
    response = reader_client.delete(recipe_detail_url)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert Recipe.objects.filter(id=recipe_id).exists()


@mark.parametrize(
    ('key'),
    (
        'tags',
        'ingredients',
        'name',
        'text',
        'cooking_time',
        'image',
    ),
)
def test_create_recipe_without_values(
    author_client,
    recipe_list_url,
    new_recipe_data,
    key,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    new_recipe_data.pop(key)
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert not Recipe.objects.count()


@mark.parametrize(
    ('key'),
    (
        'tags',
        'ingredients',
        'name',
        'text',
        'cooking_time',
    ),
)
def test_update_recipe_without_values(
    author_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
    key,
):
    new_recipe_data.pop(key)
    response = author_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    new_recipe = Recipe.objects.get(id=recipe.id)
    check_recipe_is_the_same(new_recipe, recipe)


@mark.parametrize(
    ('key', 'value'),
    (
        ('tags', [43, 213, 4]),
        ('tags', [2, '23214']),
        ('tags', [2, 2]),
        ('ingredients', [{'id': 5315, 'amount': 5}]),
        ('ingredients', [{'id': 2, 'amount': -15}]),
        ('ingredients', [{'id': 2, 'amount': 5}, {'id': 2, 'amount': 15}]),
        ('cooking_time', -15),
    ),
)
def test_create_recipe_invalid_data(
    author_client, recipe_list_url, new_recipe_data, key, value
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    new_recipe_data[key] = value
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert not Recipe.objects.count()


def test_nonexistant_recipe_update(
    author_client,
    nonexistant_recipe_url,
    new_recipe_data,
):
    assert (
        author_client.patch(
            nonexistant_recipe_url, data=new_recipe_data, format='json'
        ).status_code
        == HTTP_404_NOT_FOUND
    )


def test_nonexistant_recipe_delete(
    author_client,
    nonexistant_recipe_url,
):
    assert (
        author_client.delete(nonexistant_recipe_url).status_code
        == HTTP_404_NOT_FOUND
    )


@mark.parametrize(
    ('url'),
    (
        lf('nonexistant_tag_url'),
        lf('nonexistant_ingredient_url'),
        lf('nonexistant_recipe_url'),
        lf('nonexistant_recipe_short_link_url'),
    ),
)
def test_get_nonexistant_object(reader_client, url):
    assert reader_client.get(url).status_code == HTTP_404_NOT_FOUND
