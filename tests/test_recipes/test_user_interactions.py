import jsonschema
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from recipes.models import Recipe


def test_authorized_user_can_create_recipes(
    author_client,
    recipe_list_url,
    new_recipe_data,
    recipe_schema,
):
    assert not Recipe.objects.filter(name=new_recipe_data['name']).exists()
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_201_CREATED
    response_data = response.data
    jsonschema.validate(response_data, recipe_schema)
    assert Recipe.objects.filter(
        id=response_data['id'],
        name=new_recipe_data['name'],
    ).exists()

    recipe = Recipe.objects.get(id=response_data['id'])
    assert recipe.name == new_recipe_data['name']
    assert recipe.author == author_client.user
    assert recipe.text == new_recipe_data['text']
    assert recipe.cooking_time == new_recipe_data['cooking_time']
    assert recipe.image is not None

    tag_ids = [tag.id for tag in recipe.tags.all()]
    assert tag_ids == new_recipe_data['tags']

    ingredient_data = [
        {
            'id': recipe_ingredient.ingredient.id,
            'amount': recipe_ingredient.amount,
        }
        for recipe_ingredient in recipe.recipe_to_ingredient.all()
    ]
    assert ingredient_data == new_recipe_data['ingredients']


def test_anon_cannot_create_recipes(
    anon_client,
    recipe_list_url,
    new_recipe_data,
):
    assert not Recipe.objects.filter(name=new_recipe_data['name']).exists()
    response = anon_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Recipe.objects.filter(name=new_recipe_data['name']).exists()


def test_author_can_edit_their_recipes(
    author_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
):
    response = author_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_200_OK

    new_recipe = Recipe.objects.get(id=recipe.id)
    assert new_recipe.author == recipe.author
    assert new_recipe.image != recipe.image
    assert new_recipe.name == new_recipe_data['name']
    assert new_recipe.text == new_recipe_data['text']
    assert new_recipe.cooking_time == new_recipe_data['cooking_time']

    tag_ids = [tag.id for tag in new_recipe.tags.all()]
    assert tag_ids == new_recipe_data['tags']

    ingredient_data = [
        {
            'id': recipe_ingredient.ingredient.id,
            'amount': recipe_ingredient.amount,
        }
        for recipe_ingredient in new_recipe.recipe_to_ingredient.all()
    ]
    assert ingredient_data == new_recipe_data['ingredients']


def test_user_cannot_edit_others_recipes(
    reader_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
):
    response = reader_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_403_FORBIDDEN

    new_recipe = Recipe.objects.get(id=recipe.id)
    assert new_recipe.author == recipe.author
    assert new_recipe.image == recipe.image
    assert new_recipe.name == recipe.name
    assert new_recipe.text == recipe.text
    assert new_recipe.cooking_time == recipe.cooking_time

    tag_ids = [tag.id for tag in new_recipe.tags.all()]
    old_tag_ids = [tag.id for tag in recipe.tags.all()]
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
        for recipe_ingredient in recipe.recipe_to_ingredient.all()
    ]
    assert ingredient_data == old_ingredient_data


def test_author_can_delete_their_recipes(
    author_client,
    recipe,
    recipe_detail_url,
):
    recipe_id = recipe.id
    response = author_client.delete(recipe_detail_url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Recipe.objects.filter(id=recipe_id).exists()


def test_user_cannot_delete_others_recipes(
    reader_client,
    recipe,
    recipe_detail_url,
):
    recipe_id = recipe.id
    response = reader_client.delete(recipe_detail_url)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert Recipe.objects.filter(id=recipe_id).exists()
