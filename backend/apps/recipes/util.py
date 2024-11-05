from collections import Counter
from typing import Any, Callable, Iterable


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
