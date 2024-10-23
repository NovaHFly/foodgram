import random
import string

TOKEN_SYMBOLS = string.ascii_letters + string.digits


def generate_short_url(token_length: int = 6):
    return ''.join(random.choices(TOKEN_SYMBOLS, k=token_length))


def generate_shopping_cart(recipes) -> str:
    ingredients = {}

    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_to_ingredient.all():
            ingredient_name = recipe_ingredient.ingredient.name
            ingredient_unit = recipe_ingredient.ingredient.measurement_unit
            ingredient_amount = recipe_ingredient.amount

            if ingredient_name not in ingredients:
                ingredients[ingredient_name] = [
                    ingredient_amount,
                    ingredient_unit,
                ]
                continue

            ingredients[ingredient_name][0] += ingredient_amount

    out = ''

    for name, (unit, amount) in ingredients.items():
        out += f'{name} ({unit}) - {amount}\n'

    return out
