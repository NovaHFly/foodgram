import jsonschema
from pytest import lazy_fixture as lf, mark
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
)

from .const import NEW_AVATAR_DATA, USER_SCHEMA
from .util import check_response_is_paginated


@mark.parametrize(
    ('client', 'url', 'status'),
    (
        (lf('anon_client'), lf('users_list_url'), HTTP_200_OK),
        (lf('anon_client'), lf('author_user_url'), HTTP_200_OK),
        (lf('anon_client'), lf('current_user_url'), HTTP_401_UNAUTHORIZED),
        (lf('reader_client'), lf('users_list_url'), HTTP_200_OK),
        (lf('reader_client'), lf('author_user_url'), HTTP_200_OK),
        (lf('reader_client'), lf('current_user_url'), HTTP_200_OK),
    ),
)
def test_users_endpoints_available(client, url, status):
    assert client.get(url).status_code == status


def test_users_list_response_valid_structure(reader_client, users_list_url):
    check_response_is_paginated(reader_client.get(users_list_url))


def test_user_response_schema_is_valid(
    reader_client,
    author_user_url,
):
    jsonschema.validate(reader_client.get(author_user_url).data, USER_SCHEMA)


def test_can_add_avatar(reader_client, avatar_url):
    old_avatar = reader_client.user.avatar
    assert (
        reader_client.put(
            avatar_url,
            data=NEW_AVATAR_DATA,
            format='json',
        ).status_code
        == HTTP_200_OK
    )
    reader_client.user.refresh_from_db()
    assert reader_client.user.avatar is not old_avatar


def test_can_delete_avatar(reader_client, avatar_url):
    assert reader_client.user.avatar
    assert reader_client.delete(avatar_url).status_code == HTTP_204_NO_CONTENT
    reader_client.user.refresh_from_db()
    assert not reader_client.user.avatar


def test_anon_cannot_access_avatar_endpoints(
    anon_client,
    avatar_url,
):
    assert (
        anon_client.put(
            avatar_url, data=NEW_AVATAR_DATA, format='json'
        ).status_code
        == HTTP_401_UNAUTHORIZED
    )
    assert anon_client.delete(avatar_url).status_code == HTTP_401_UNAUTHORIZED
