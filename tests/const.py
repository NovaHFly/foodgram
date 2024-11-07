from django.core.files.uploadedfile import SimpleUploadedFile

RANDOM_NAME_POOL = (
    'test',
    'another',
    'hello',
    'cat',
    'many',
    'job',
    'dog',
    'carrot',
)

SHOPPING_LIST_REGEX = r'(.+) \((\d+)\)'

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)

GIF_BASE64 = (
    'data:image/gif;base64,'
    'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
)
ANOTHER_GIF_BASE64 = (
    'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
)

SOME_IMAGE = SimpleUploadedFile(
    'small.gif',
    SMALL_GIF,
    content_type='image/gif',
)

NEW_AVATAR_DATA = {'avatar': ANOTHER_GIF_BASE64}


USER_SCHEMA = {
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


TAG_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'name': {'type': 'string'},
        'slug': {'type': 'string'},
    },
}


INGREDIENT_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'name': {'type': 'string'},
        'measurement_unit': {'type': 'string'},
    },
}


RECIPE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'tags': {
            'type': 'array',
            'items': TAG_SCHEMA,
        },
        'ingredients': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': INGREDIENT_SCHEMA['properties']
                | {'amount': {'type': 'number'}},
            },
        },
        'author': USER_SCHEMA,
        'name': {'type': 'string'},
        'image': {'type': 'string'},
        'text': {'type': 'string'},
        'cooking_time': {'type': 'number'},
    },
}


SHORT_RECIPE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'name': {'type': 'string'},
        'image': {'type': 'string'},
        'cooking_time': {'type': 'number'},
    },
}


SUBSCRIPTION_USER_SCHEMA = USER_SCHEMA.copy()
SUBSCRIPTION_USER_SCHEMA['properties'] |= {
    'recipes': {
        'type': 'array',
        'items': SHORT_RECIPE_SCHEMA,
    },
    'recipes_count': {'type': 'number'},
}
