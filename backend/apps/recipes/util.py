import re
from collections import Counter
from itertools import chain
from typing import Any, Callable, Iterable

from .models import Recipe

URL_REGEX = re.compile(r'(https?:\/\/[\w\d\-_.]+)')


def generate_shopping_list(recipes: Iterable[Recipe]) -> str:
    """Generate text content of shopping list file.

    Args:
        recipes (Iterable[Recipe]): Collection of recipes.

    Returns:
        str: Shopping list
    """

    recipe_ingredients = chain(
        *(recipe.recipe_to_ingredient.all() for recipe in recipes)
    )

    ingredients = {}
    for recipe_ingredient in recipe_ingredients:
        ingredient_name = recipe_ingredient.ingredient.name
        ingredient_unit = recipe_ingredient.ingredient.measurement_unit
        ingredient_amount = recipe_ingredient.amount

        if ingredient_name in ingredients:
            ingredients[ingredient_name][0] += ingredient_amount
            continue

        ingredients[ingredient_name] = [
            ingredient_amount,
            ingredient_unit,
        ]

    return '\n'.join(
        f'{name} ({unit}) - {amount}'
        for name, (unit, amount) in ingredients.items()
    )


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


def extract_host_with_schema(url: str) -> str:
    """Extract schema and hostname from url."""
    return URL_REGEX.match(url)[0]
