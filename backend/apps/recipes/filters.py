import django_filters
from django.db.models import QuerySet

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

    def _check_current_user_in_lookup(
        self,
        lookup: str,
        queryset: QuerySet,
        value: int,
    ) -> QuerySet:
        if self.request.user.is_anonymous:
            return queryset.none()

        lookup_params = {lookup + '__in': [self.request.user]}
        if not value:
            return queryset.exclude(**lookup_params)
        return queryset.filter(**lookup_params)

    def favorited_by_current_user(
        self,
        queryset: QuerySet,
        name: str,
        value: int,
    ) -> QuerySet:
        return self._check_current_user_in_lookup(
            'favorited_by_users',
            queryset,
            value,
        )

    def in_current_user_shopping_cart(
        self,
        queryset: QuerySet,
        name: str,
        value: int,
    ) -> QuerySet:
        return self._check_current_user_in_lookup(
            'shoppingcart__user',
            queryset,
            value,
        )
