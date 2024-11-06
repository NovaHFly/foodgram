import random
from collections import Counter
from typing import Any, Callable, Iterable

from .const import TOKEN_SYMBOLS


def generate_token(token_length: int = 6) -> str:
    """Generate random string of specified length.

    Args:
        token_length (int): Token length.

    Returns:
        str: Token.
    """
    return ''.join(random.choices(TOKEN_SYMBOLS, k=token_length))


def contains_duplicates(
    collection: Iterable,
    key: Callable[[Any], Any] = lambda x: x,
) -> bool:
    """Check if collection contains duplicate items.

    Args:
        collection [Iterable]: Collection which can be iterated over.
        key [Callable]: Function which returns key used to check for duplicate.

    Returns:
        bool: True if collection contains duplicate items.
    """

    _collection = map(key, collection)
    counter = Counter(_collection)
    return counter.most_common(1)[0][1] > 1
