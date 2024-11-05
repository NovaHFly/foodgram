from django.contrib import admin

from recipes.admin import RecipeAdmin

from .models import UserFavorites


@admin.register(UserFavorites)
class UserFavoritesAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']
    filter_horizontal = ['recipes']


RecipeAdmin.favorited_count = (
    lambda self, obj: obj.favorites_lists.count()
)
RecipeAdmin.favorited_count.__name__ = 'Раз добавлен в избранное'
RecipeAdmin.list_display += ['favorited_count']
