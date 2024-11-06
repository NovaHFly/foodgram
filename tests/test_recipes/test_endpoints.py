import jsonschema
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_200_OK,
)

pytestmark = mark.depends(name='recipes_endpoints_valid')


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
    response = client.get(url)
    jsonschema.validate(response.data, schema)


def test_recipe_list_response_valid_structure(reader_client, recipe_list_url):
    response = reader_client.get(recipe_list_url)
    assert all(
        key in response.data
        for key in (
            'count',
            'next',
            'previous',
            'results',
        )
    )
