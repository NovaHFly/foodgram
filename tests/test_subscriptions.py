import jsonschema
from django.conf import settings
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from .const import SUBSCRIPTION_USER_SCHEMA
from .util import check_different_pages, check_response_is_paginated


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


def test_subscription_list_is_paginated(
    reader_client,
    subscription_list_url,
):
    check_response_is_paginated(reader_client.get(subscription_list_url))


@mark.usefixtures('add_many_subscriptions')
def test_subscription_list_different_pages(
    reader_client, subscription_list_url
):
    check_different_pages(reader_client, subscription_list_url)


@mark.usefixtures('add_many_subscriptions')
@mark.parametrize(
    ('query', 'length'),
    (
        ('', settings.REST_FRAMEWORK['PAGE_SIZE']),
        ('?limit=5', 5),
        ('?limit=1', 1),
        ('?limit=15', 15),
    ),
)
def test_subscription_list_page_size(
    reader_client,
    subscription_list_url,
    query,
    length,
):
    assert (
        len(reader_client.get(subscription_list_url + query).data['results'])
        == length
    )


@mark.usefixtures('subscribe_reader_to_author', 'recipe')
def test_subscription_user_schema_valid(
    reader_client,
    subscription_list_url,
):
    jsonschema.validate(
        reader_client.get(subscription_list_url).data['results'][0],
        SUBSCRIPTION_USER_SCHEMA,
    )


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
    assert len(response.data['results'][0]['recipes']) <= limit


def test_anon_cannot_subscribe(anon_client, author_subscribe_url):
    assert (
        anon_client.post(author_subscribe_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_anon_cannot_unsubscribe(anon_client, author_subscribe_url):
    assert (
        anon_client.delete(author_subscribe_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_user_can_subscribe_to_someone(
    reader_client,
    author_user,
    author_subscribe_url,
):
    response = reader_client.post(author_subscribe_url)
    assert response.status_code == HTTP_201_CREATED
    assert author_user in reader_client.user.subscription_list.users.all()


@mark.usefixtures('subscribe_reader_to_author')
def test_user_can_unsubscribe_from_someone(
    reader_client,
    author_user,
    author_subscribe_url,
):
    response = reader_client.delete(author_subscribe_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert author_user not in reader_client.user.subscription_list.users.all()


def test_user_cannot_subscribe_to_themselves(
    reader_client,
    reader_subscribe_url,
):
    response = reader_client.post(reader_subscribe_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert (
        reader_client.user
        not in reader_client.user.subscription_list.users.all()
    )


@mark.usefixtures('subscribe_reader_to_author')
def test_user_cannot_subscribe_twice(
    reader_client,
    author_subscribe_url,
):
    assert reader_client.user.subscription_list.users.count() == 1
    response = reader_client.post(author_subscribe_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert reader_client.user.subscription_list.users.count() == 1


def test_user_cannot_unsubscribe_when_not_subscribed(
    reader_client,
    author_subscribe_url,
):
    assert reader_client.user.subscription_list.users.count() == 0
    response = reader_client.delete(author_subscribe_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert reader_client.user.subscription_list.users.count() == 0


@mark.parametrize(
    ('usefixture', 'is_subscribed'),
    (
        ('', False),
        (lf('subscribe_reader_to_author'), True),
    ),
)
def test_is_subscribed_key_in_user_schema(
    reader_client, author_user_url, is_subscribed, usefixture
):
    response = reader_client.get(author_user_url)
    assert 'is_subscribed' in response.data
    assert response.data['is_subscribed'] == is_subscribed


@mark.parametrize(('method'), ('POST', 'DELETE'))
def test_subcribe_nonexistant_user(
    reader_client,
    nonexistant_user_subscribe_url,
    method,
):
    assert (
        reader_client.generic(
            method,
            nonexistant_user_subscribe_url,
        ).status_code
        == HTTP_404_NOT_FOUND
    )
