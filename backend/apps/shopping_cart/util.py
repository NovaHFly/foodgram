from itertools import chain
from typing import Iterable

from recipes.models import Recipe


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
