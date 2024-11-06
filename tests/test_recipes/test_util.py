from pytest import mark

from recipes.util import contains_duplicates


@mark.parametrize(
    ('test_data', 'key', 'result'),
    (
        ([1, 2, 3, 1], lambda x: x, True),
        ([1, 2, 'test', 3], lambda x: x, False),
        ([1, 2, 3, 4, 1, 1, 2, 3, 1], lambda x: x, True),
        ([{'id': 1}, {'id': 2}, {'id': 3}], lambda x: x['id'], False),
        ([{'id': 1}, {'id': 2}, {'id': 1}], lambda x: x['id'], True),
    ),
)
def test_contains_duplicates(test_data, key, result):
    assert contains_duplicates(test_data, key=key) is result
