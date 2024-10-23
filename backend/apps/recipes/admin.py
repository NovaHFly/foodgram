from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    ShortLink,
    Tag,
)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
        'name',
    )
    list_display_links = ('id', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
    )
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author')
    inlines = (RecipeIngredientInline,)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_url', 'full_url')
    list_display_links = ('id', 'short_url')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_display_links = ('id', 'user')
