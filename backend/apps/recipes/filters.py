import django_filters

from .const import BOOLEAN_NUMBER_CHOICES
from .models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(
        lookup_expr='id',
    )
    is_favorited = django_filters.TypedChoiceFilter(
        choices=BOOLEAN_NUMBER_CHOICES,
        method='favorited_by_current_user',
        coerce=int,
    )
    is_in_shopping_cart = django_filters.TypedChoiceFilter(
        choices=BOOLEAN_NUMBER_CHOICES,
        method='in_current_user_shopping_cart',
        coerce=int,
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    # TODO: Duplicate code
    def favorited_by_current_user(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        value = int(value)
        if not value:
            return queryset.exclude(favorited_by_users__in=[self.request.user])
        return queryset.filter(favorited_by_users__in=[self.request.user])

    def in_current_user_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        value = int(value)
        if not value:
            return queryset.exclude(shoppingcart__user__in=[self.request.user])
        return queryset.filter(shoppingcart__user__in=[self.request.user])
