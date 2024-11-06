from pytest import mark

from common.const import TOKEN_SYMBOLS
from common.util import generate_token


@mark.parametrize(('length'), (5, 10, 15, 20))
def test_generated_token_is_valid(length):
    token = generate_token(length)
    assert len(token) == length
    assert all(sym in TOKEN_SYMBOLS for sym in token)
