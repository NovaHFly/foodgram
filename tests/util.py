import re
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient

from common.util import contains_duplicates
from recipes.models import Ingredient, Recipe, Tag

from .const import SHOPPING_LIST_REGEX

User = get_user_model()


def create_user(
    username: str, avatar: Optional[SimpleUploadedFile] = None
) -> AbstractUser:
    return User.objects.create(
        username=username,
        email=f'{username}@foodgram.com',
        first_name=username,
        last_name='user',
        avatar=avatar,
    )


def create_user_client(user: AbstractUser) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    client.user = user
    return client


def create_recipe(
    recipe_data: dict,
    tags: Iterable[Tag],
    ingredients_with_amounts: Iterable[tuple[Ingredient, int]],
):
    recipe = Recipe.objects.create(**recipe_data)
    for tag in tags:
        recipe.tags.add(tag)
    for ingredient, amount in ingredients_with_amounts:
        recipe.ingredients.add(ingredient, through_defaults={'amount': amount})
    recipe.save()
    return recipe


def check_response_is_paginated(response: Response) -> None:
    assert all(
        key in response.data
        for key in (
            'count',
            'next',
            'previous',
            'results',
        )
    )


def check_different_pages(
    client: APIClient,
    url: str,
):
    page1_data = client.get(url).data['results']
    page2_response = client.get(url + '?page=2')
    assert page2_response.status_code == HTTP_200_OK
    page2_data = page2_response.data['results']
    assert page1_data != page2_data
    assert not contains_duplicates(
        page1_data + page2_data,
        key=lambda x: x['id'],
    )


def check_recipe_is_the_same(new_recipe: Recipe, old_recipe: Recipe):
    assert new_recipe.author == old_recipe.author
    assert new_recipe.image == old_recipe.image
    assert new_recipe.name == old_recipe.name
    assert new_recipe.text == old_recipe.text
    assert new_recipe.cooking_time == old_recipe.cooking_time

    tag_ids = [tag.id for tag in new_recipe.tags.all()]
    old_tag_ids = [tag.id for tag in old_recipe.tags.all()]
    assert tag_ids == old_tag_ids

    ingredient_data = [
        {
            'id': recipe_ingredient.ingredient.id,
            'amount': recipe_ingredient.amount,
        }
        for recipe_ingredient in new_recipe.recipe_to_ingredient.all()
    ]
    old_ingredient_data = [
        {
            'id': recipe_ingredient.ingredient.id,
            'amount': recipe_ingredient.amount,
        }
        for recipe_ingredient in old_recipe.recipe_to_ingredient.all()
    ]
    assert ingredient_data == old_ingredient_data


def check_recipe_updated(recipe: Recipe, data: dict):
    assert recipe.author == data['author']
    assert recipe.name == data['name']
    assert recipe.text == data['text']
    assert recipe.cooking_time == data['cooking_time']

    tag_ids = [tag.id for tag in recipe.tags.all()]
    assert tag_ids == data['tags']

    ingredient_data = [
        {
            'id': recipe_ingredient.ingredient.id,
            'amount': recipe_ingredient.amount,
        }
        for recipe_ingredient in recipe.recipe_to_ingredient.all()
    ]
    assert ingredient_data == data['ingredients']


def parse_shopping_list(shopping_list: str) -> list[tuple[str, int]]:
    return [
        (match[1], int(match[2]))
        for match in re.finditer(
            SHOPPING_LIST_REGEX,
            shopping_list,
        )
    ]
