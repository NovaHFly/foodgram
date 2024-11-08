import re

from pytest import lazy_fixture as lf, mark
from pytest_django.asserts import assertRedirects
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from short_link.models import ShortLink
from short_link.util import extract_host_with_schema

from .const import RECIPE_PATH_REGEX, SHORT_LINK_REGEX


@mark.parametrize(
    ('input', 'expected'),
    (
        (
            'https://docs.djangoproject.com/en/dev/topics/testing/tools/#django.test.SimpleTestCase.assertRedirects',
            'https://docs.djangoproject.com',
        ),
        (
            'https://www.google.com/search?q=html+anchor+download',
            'https://www.google.com',
        ),
        (
            'http://www.example.org',
            'http://www.example.org',
        ),
        (
            'https://htmlbook.ru/html/a/name',
            'https://htmlbook.ru',
        ),
    ),
)
def test_extract_host(input, expected):
    assert extract_host_with_schema(input) == expected


@mark.parametrize(
    ('client', 'url'),
    (
        (lf('anon_client'), lf('recipe_get_link_url')),
        (lf('reader_client'), lf('recipe_get_link_url')),
    ),
)
def test_short_link_endpoints_available(client, url):
    assert client.get(url).status_code == HTTP_200_OK


def test_short_link_valid(reader_client, recipe_get_link_url):
    response = reader_client.get(recipe_get_link_url)
    assert 'short-link' in response.data
    assert (match := re.match(SHORT_LINK_REGEX, response.data['short-link']))
    assert (short_link_object := ShortLink.objects.get(short_token=match[1]))
    assert re.match(RECIPE_PATH_REGEX, short_link_object.full_path)


def test_short_link_redirect_valid(reader_client, recipe_get_link_url):
    short_link = reader_client.get(recipe_get_link_url).data['short-link']
    resource_path = ShortLink.objects.get(
        short_token=re.match(SHORT_LINK_REGEX, short_link)[1]
    ).full_path
    full_url = f'{extract_host_with_schema(short_link)}/{resource_path}'

    redirect_response = reader_client.get(short_link)
    assertRedirects(
        redirect_response,
        full_url,
        target_status_code=HTTP_404_NOT_FOUND,
    )
