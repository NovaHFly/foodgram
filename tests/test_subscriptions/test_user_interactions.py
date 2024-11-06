from pytest import mark
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)


def test_anon_cannot_subscribe(anon_client, subscribe_to_author_url):
    assert (
        anon_client.post(subscribe_to_author_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_anon_cannot_unsubscribe(anon_client, subscribe_to_author_url):
    assert (
        anon_client.delete(subscribe_to_author_url).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_user_can_subscribe_to_someone(
    reader_client,
    author_user,
    subscribe_to_author_url,
):
    response = reader_client.post(subscribe_to_author_url)
    assert response.status_code == HTTP_201_CREATED
    assert author_user in reader_client.user.subscription_list.users.all()


@mark.usefixtures('subscribe_reader_to_author')
def test_user_can_unsubscribe_from_someone(
    reader_client,
    author_user,
    subscribe_to_author_url,
):
    response = reader_client.delete(subscribe_to_author_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert author_user not in reader_client.user.subscription_list.users.all()


def test_user_cannot_subscribe_to_themselves(
    reader_client,
    subscribe_to_reader_url,
):
    response = reader_client.post(subscribe_to_reader_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert (
        reader_client.user
        not in reader_client.user.subscription_list.users.all()
    )


@mark.usefixtures('subscribe_reader_to_author')
def test_user_cannot_subscribe_twice(
    reader_client,
    subscribe_to_author_url,
):
    assert reader_client.user.subscription_list.users.count() == 1
    response = reader_client.post(subscribe_to_author_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert reader_client.user.subscription_list.users.count() == 1


def test_user_cannot_unsubscribe_when_not_subscribed(
    reader_client,
    subscribe_to_author_url,
):
    assert reader_client.user.subscription_list.users.count() == 0
    response = reader_client.delete(subscribe_to_author_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert reader_client.user.subscription_list.users.count() == 0
