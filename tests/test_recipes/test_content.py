from pytest import lazy_fixture as lf, mark

from recipes.models import Recipe

pytestmark = mark.depends(on=['recipes_endpoints_valid'])


@mark.parametrize(
    ('url', '_create_data'),
    (
        (
            lf('tag_list_url'),
            lf('create_many_tags'),
        ),
        (
            lf('ingredient_list_url'),
            lf('create_many_ingredients'),
        ),
    ),
)
def test_tag_ingredient_ordering(reader_client, url, _create_data):
    data = reader_client.get(url).data
    assert sorted(data, key=lambda x: x['name']) == data


@mark.depends(on=['recipe_list_supports_custom_page_size'])
@mark.usefixtures('create_many_recipes')
def test_recipe_ordering(reader_client, recipe_list_url):
    data = reader_client.get(recipe_list_url + '?limit=50').data['results']
    pub_dates = [
        Recipe.objects.get(id=recipe['id']).pub_date for recipe in data
    ]
    assert sorted(pub_dates, reverse=True) == pub_dates
