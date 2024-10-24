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
        'name',
        'measurement_unit',
    )
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'name',
    )
    list_display_links = ('slug',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'full_url')
    list_display_links = ('short_url',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    list_display_links = ('user',)
