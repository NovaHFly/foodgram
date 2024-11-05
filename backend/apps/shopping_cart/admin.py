from django.contrib import admin

from users.admin import UserAdmin

from .models import ShoppingCart


class ShoppingCartInline(admin.StackedInline):
    model = ShoppingCart
    filter_horizontal = ['recipes']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']
    filter_horizontal = ['recipes']


UserAdmin.inlines += [ShoppingCartInline]
