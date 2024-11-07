import re

import jsonschema
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from common.util import contains_duplicates

from .const import SHOPPING_LIST_REGEX
from .util import parse_shopping_list


def test_can_add_recipe_to_cart(
    reader_client, recipe_shopping_cart_url, recipe, short_recipe_schema
):
    response = reader_client.post(recipe_shopping_cart_url)
    assert response.status_code == HTTP_201_CREATED
    jsonschema.validate(response.data, short_recipe_schema)
    assert recipe in reader_client.user.shopping_cart.recipes.all()


@mark.usefixtures('add_recipe_to_reader_shopping_cart')
def test_can_remove_recipe_from_cart(
    reader_client,
    recipe_shopping_cart_url,
    recipe,
):
    response = reader_client.delete(recipe_shopping_cart_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert recipe not in reader_client.user.shopping_cart.recipes.all()


@mark.usefixtures('add_recipe_to_reader_shopping_cart')
def test_cannot_add_to_cart_twice(reader_client, recipe_shopping_cart_url):
    assert (
        reader_client.post(recipe_shopping_cart_url).status_code
        == HTTP_400_BAD_REQUEST
    )
    assert not contains_duplicates(
        reader_client.user.shopping_cart.recipes.all()
    )


def test_cannot_remove_from_cart_if_not_added(
    reader_client, recipe_shopping_cart_url
):
    assert (
        reader_client.delete(recipe_shopping_cart_url).status_code
        == HTTP_400_BAD_REQUEST
    )


def test_anon_cannot_add_to_cart(anon_client, recipe_shopping_cart_url):
    assert (
        anon_client.post(recipe_shopping_cart_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_anon_cannot_remove_from_cart(anon_client, recipe_shopping_cart_url):
    assert (
        anon_client.delete(recipe_shopping_cart_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


@mark.parametrize(
    ('is_in_shopping_cart', 'usefixtures'),
    (
        (False, ''),
        (True, lf('add_recipe_to_reader_shopping_cart')),
    ),
)
def test_is_in_shopping_cart_key(
    reader_client,
    recipe_detail_url,
    is_in_shopping_cart,
    usefixtures,
):
    response = reader_client.get(recipe_detail_url)
    assert 'is_in_shopping_cart' in response.data
    assert response.data['is_in_shopping_cart'] == is_in_shopping_cart


@mark.usefixtures('add_random_recipes_to_reader_shopping_cart')
@mark.parametrize(('is_in_shopping_cart'), (False, True))
def test_filter_recipes_by_shopping_cart(
    reader_client,
    recipe_list_url,
    is_in_shopping_cart,
):
    query = f'?is_in_shopping_cart={int(is_in_shopping_cart)}'
    response = reader_client.get(recipe_list_url + query)
    assert all(
        recipe['is_in_shopping_cart'] == is_in_shopping_cart
        for recipe in response.data['results']
    )


def test_can_download_shopping_list(
    reader_client,
    download_shopping_cart_url,
):
    response = reader_client.get(download_shopping_cart_url)
    assert response.status_code == HTTP_200_OK
    assert response.headers['Content-Type'] == 'text/plain; charset=UTF-8'


@mark.usefixtures(
    'create_recipes_with_overlapping_ingredients',
    'add_all_recipes_to_reader_shopping_cart',
)
def test_shopping_list_is_valid(
    reader_client,
    download_shopping_cart_url,
):
    assert re.search(
        SHOPPING_LIST_REGEX,
        reader_client.get(download_shopping_cart_url).content.decode(),
    )


@mark.usefixtures(
    'create_recipes_with_overlapping_ingredients',
    'add_all_recipes_to_reader_shopping_cart',
)
def test_ingredients_are_summed_up(
    reader_client,
    download_shopping_cart_url,
):
    ingredients_with_amounts = parse_shopping_list(
        reader_client.get(download_shopping_cart_url).content.decode()
    )
    assert not contains_duplicates(
        ingredients_with_amounts, key=lambda x: x[0]
    )
    assert any(
        ingredient_with_amount[1] > 50
        for ingredient_with_amount in ingredients_with_amounts
    )


@mark.parametrize(('method'), ('POST', 'DELETE'))
def test_shopping_cart_nonexistant_recipe(
    reader_client,
    nonexistant_recipe_shopping_cart_url,
    method,
):
    assert (
        reader_client.generic(
            method,
            nonexistant_recipe_shopping_cart_url,
        ).status_code
        == HTTP_404_NOT_FOUND
    )
