import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from pytest import fixture
from rest_framework.test import APIClient

PASSWORD = 'S3cre7P@ssw0rd'
NEW_PASSWORD = 'N3wS3cre7P@ssw0rd'

User = get_user_model()


def create_user(
    username: str,
) -> tuple[AbstractUser]:
    user = User.objects.create(
        username=username,
        email=f'{username}@foodgram.com',
        first_name=username,
        last_name='user',
    )
    user.set_password(PASSWORD)
    user.save()
    return user


def _create_user_client(user: AbstractUser) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    client.user = user
    return client


@fixture(scope='session', autouse=True)
def setup_media_root():
    settings.MEDIA_ROOT = tempfile.mkdtemp()
    yield
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


@fixture
def reader_user():
    return create_user('regular')


@fixture
def author_user():
    return create_user('author')


@fixture
def anon_client():
    return APIClient()


@fixture
def reader_client(reader_user):
    return _create_user_client(reader_user)


@fixture
def author_client(author_user):
    return _create_user_client(author_user)


@fixture
def user_schema():
    return {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'email': {'type': 'string'},
            'username': {'type': 'string'},
            'first_name': {'type': 'string'},
            'last_name': {'type': 'string'},
            'avatar': {'type': ['string', 'null']},
        },
    }


@fixture
def small_gif():
    return (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )


@fixture
def gif_base64():
    return (
        'data:image/gif;base64,'
        'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    )


@fixture
def another_gif_base64():
    return (
        'data:image/gif;base64,'
        'R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
    )
