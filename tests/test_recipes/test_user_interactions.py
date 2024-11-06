from pytest import mark
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from recipes.models import Recipe


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


def test_authorized_user_can_create_recipes(
    author_client,
    recipe_list_url,
    new_recipe_data,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_201_CREATED
    response_data = response.data
    assert (
        Recipe.objects.count()
        and Recipe.objects.filter(id=response_data['id']).exists()
    )

    recipe = Recipe.objects.get(id=response_data['id'])
    assert recipe.image is not None
    check_recipe_updated(
        recipe,
        new_recipe_data | {'author': author_client.user},
    )


def test_anon_cannot_create_recipes(
    anon_client,
    recipe_list_url,
    new_recipe_data,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    response = anon_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert not Recipe.objects.count()


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
    assert new_recipe.image != recipe.image
    check_recipe_updated(
        new_recipe,
        new_recipe_data | {'author': recipe.author},
    )


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
    check_recipe_is_the_same(new_recipe, recipe)


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


@mark.parametrize(
    ('key'),
    (
        'tags',
        'ingredients',
        'name',
        'text',
        'cooking_time',
        'image',
    ),
)
def test_create_recipe_without_values(
    author_client,
    recipe_list_url,
    new_recipe_data,
    key,
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    new_recipe_data.pop(key)
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert not Recipe.objects.count()


@mark.parametrize(
    ('key'),
    (
        'tags',
        'ingredients',
        'name',
        'text',
        'cooking_time',
    ),
)
def test_update_recipe_without_values(
    author_client,
    recipe,
    recipe_detail_url,
    new_recipe_data,
    key,
):
    new_recipe_data.pop(key)
    response = author_client.patch(
        recipe_detail_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    new_recipe = Recipe.objects.get(id=recipe.id)
    check_recipe_is_the_same(new_recipe, recipe)


@mark.parametrize(
    ('key', 'value'),
    (
        ('tags', [43, 213, 4]),
        ('tags', [2, '23214']),
        ('tags', [2, 2]),
        ('ingredients', [{'id': 5315, 'amount': 5}]),
        ('ingredients', [{'id': 2, 'amount': -15}]),
        ('ingredients', [{'id': 2, 'amount': 5}, {'id': 2, 'amount': 15}]),
        ('cooking_time', -15),
    ),
)
def test_create_recipe_invalid_data(
    author_client, recipe_list_url, new_recipe_data, key, value
):
    Recipe.objects.all().delete()
    assert not Recipe.objects.count()
    new_recipe_data[key] = value
    response = author_client.post(
        recipe_list_url,
        data=new_recipe_data,
        format='json',
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert not Recipe.objects.count()
