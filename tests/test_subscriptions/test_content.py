from django.conf import settings
from pytest import mark

pytestmark = mark.depends(on='subscriptions_endpoints_valid')


@mark.usefixtures('add_many_subscriptions')
def test_subscriptions_list_default_page_size(
    reader_client,
    subscription_list_url,
):
    response = reader_client.get(subscription_list_url)
    assert (
        len(response.data['results']) == settings.REST_FRAMEWORK['PAGE_SIZE']
    )


@mark.usefixtures('add_many_subscriptions')
def test_subscriptions_list_custom_page_size(
    reader_client,
    subscription_list_url,
):
    response = reader_client.get(subscription_list_url + '?limit=5')
    assert len(response.data['results']) == 5


@mark.usefixtures('add_many_subscriptions')
def test_subscription_list_other_pages(reader_client, subscription_list_url):
    response = reader_client.get(subscription_list_url)
    page_1_data = response.data['results']
    response = reader_client.get(subscription_list_url + '?page=2')
    page_2_data = response.data['results']
    assert page_2_data
    assert page_2_data != page_1_data


@mark.usefixtures('subscribe_reader_to_author', 'create_many_recipes')
@mark.parametrize(('limit'), (0, 2, 4))
def test_limit_recipes_count_in_subscription_list(
    reader_client,
    subscription_list_url,
    limit,
):
    response = reader_client.get(
        subscription_list_url + f'?recipes_limit={limit}'
    )
    assert len(response.data['results'][0]['recipes']) == limit
