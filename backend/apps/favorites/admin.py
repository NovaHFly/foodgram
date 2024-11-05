from django.contrib import admin

from recipes.admin import RecipeAdmin
from users.admin import UserAdmin

from .models import UserFavorites


class UserFavoritesInline(admin.StackedInline):
    model = UserFavorites
    filter_horizontal = ['recipes']


@admin.register(UserFavorites)
class UserFavoritesAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']
    filter_horizontal = ['recipes']


RecipeAdmin.favorited_count = lambda self, obj: obj.favorites_lists.count()
RecipeAdmin.favorited_count.__name__ = 'Раз добавлен в избранное'
RecipeAdmin.list_display += ['favorited_count']

UserAdmin.inlines += [UserFavoritesInline]
