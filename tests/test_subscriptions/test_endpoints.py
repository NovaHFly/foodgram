import jsonschema
from pytest import lazy_fixture as lf, mark
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

pytestmark = [mark.depends(name='subscriptions_endpoints_valid')]


@mark.parametrize(
    ('client', 'url', 'status'),
    (
        (
            lf('anon_client'),
            lf('subscription_list_url'),
            HTTP_401_UNAUTHORIZED,
        ),
        (
            lf('reader_client'),
            lf('subscription_list_url'),
            HTTP_200_OK,
        ),
    ),
)
def test_subscription_endpoints_available(client, url, status):
    assert client.get(url).status_code == status


@mark.depends(on='test_subscription_endpoints_available')
def test_subscription_list_response_structure_valid(
    reader_client,
    subscription_list_url,
):
    response = reader_client.get(subscription_list_url)
    print(response.data)
    assert all(
        (
            key in response.data
            for key in (
                'count',
                'next',
                'previous',
                'results',
            )
        )
    )


@mark.usefixtures('subscribe_reader_to_author', 'recipe')
@mark.depends(on='test_subscription_list_response_structure_valid')
def test_subscription_list_user_schema_valid(
    reader_client,
    subscription_list_url,
    subscription_user_schema,
):
    response = reader_client.get(subscription_list_url)
    single_user_json = response.data['results'][0]
    jsonschema.validate(single_user_json, subscription_user_schema)
