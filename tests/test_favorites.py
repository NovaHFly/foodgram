import jsonschema
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from common.util import contains_duplicates


def test_can_add_recipe_to_favorites(
    reader_client, recipe_favorite_url, recipe, short_recipe_schema
):
    response = reader_client.post(recipe_favorite_url)
    assert response.status_code == HTTP_201_CREATED
    jsonschema.validate(response.data, short_recipe_schema)
    assert recipe in reader_client.user.favorites_list.recipes.all()


@mark.usefixtures('add_recipe_to_reader_favorites')
def test_can_remove_recipe_from_favorites(
    reader_client,
    recipe_favorite_url,
    recipe,
):
    response = reader_client.delete(recipe_favorite_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert recipe not in reader_client.user.favorites_list.recipes.all()


@mark.usefixtures('add_recipe_to_reader_favorites')
def test_cannot_favorite_twice(reader_client, recipe_favorite_url):
    assert (
        reader_client.post(recipe_favorite_url).status_code
        == HTTP_400_BAD_REQUEST
    )
    assert not contains_duplicates(
        reader_client.user.favorites_list.recipes.all()
    )


def test_cannot_unfavorite_not_favorited(reader_client, recipe_favorite_url):
    assert (
        reader_client.delete(recipe_favorite_url).status_code
        == HTTP_400_BAD_REQUEST
    )


def test_anon_cannot_favorite_recipe(anon_client, recipe_favorite_url):
    assert (
        anon_client.post(recipe_favorite_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_anon_cannot_unfavorite_recipe(anon_client, recipe_favorite_url):
    assert (
        anon_client.delete(recipe_favorite_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


@mark.parametrize(
    ('is_favorited', 'usefixtures'),
    (
        (False, ''),
        (True, lf('add_recipe_to_reader_favorites')),
    ),
)
def test_is_favorited_key(
    reader_client,
    recipe_detail_url,
    is_favorited,
    usefixtures,
):
    response = reader_client.get(recipe_detail_url)
    assert 'is_favorited' in response.data
    assert response.data['is_favorited'] == is_favorited


@mark.usefixtures('add_random_recipes_to_reader_favorites')
@mark.parametrize(('is_favorited'), (False, True))
def test_filter_recipes_by_favorite(
    reader_client,
    recipe_list_url,
    is_favorited,
):
    query = f'?is_favorited={int(is_favorited)}'
    response = reader_client.get(recipe_list_url + query)
    assert all(
        recipe['is_favorited'] == is_favorited
        for recipe in response.data['results']
    )


@mark.parametrize(('method'), ('POST', 'DELETE'))
def test_favorite_nonexistant_recipe(
    reader_client,
    nonexistant_recipe_favorite_url,
    method,
):
    assert (
        reader_client.generic(
            method,
            nonexistant_recipe_favorite_url,
        ).status_code
        == HTTP_404_NOT_FOUND
    )
