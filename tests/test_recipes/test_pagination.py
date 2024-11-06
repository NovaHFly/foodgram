from django.conf import settings
from pytest import mark

pytestmark = [
    mark.depends(on=['endpoints_valid']),
    mark.usefixtures('create_many_recipes'),
]


@mark.depends(name='recipe_list_valid_response')
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


@mark.depends(on=['test_recipe_list_response_valid_structure'])
def test_recipe_list_default_page_size(reader_client, recipe_list_url):
    response = reader_client.get(recipe_list_url)
    assert (
        len(response.data['results']) == settings.REST_FRAMEWORK['PAGE_SIZE']
    )


@mark.depends(
    name='recipe_list_supports_custom_page_size',
    on=['test_recipe_list_response_valid_structure'],
)
def test_recipe_list_custom_page_size(reader_client, recipe_list_url):
    response = reader_client.get(recipe_list_url + '?limit=5')
    assert len(response.data['results']) == 5


@mark.depends(on=['test_recipe_list_response_valid_structure'])
def test_recipe_list_other_pages(reader_client, recipe_list_url):
    response = reader_client.get(recipe_list_url)
    page_1_data = response.data['results']
    response = reader_client.get(recipe_list_url + '?page=2')
    page_2_data = response.data['results']
    assert page_2_data
    assert page_2_data != page_1_data
