from django.db.models import QuerySet
from django_filters import TypedChoiceFilter

from common.const import BOOLEAN_NUMBER_CHOICES
from recipes.filters import RecipeFilter


def is_in_current_user_shopping_cart(
    self, queryset: QuerySet, name: str, value: int
) -> QuerySet:
    if self.request.user.is_anonymous:
        return queryset.none()

    lookup_params = {'shopping_carts__user__in': [self.request.user]}
    if not value:
        return queryset.exclude(**lookup_params)
    return queryset.filter(**lookup_params)


RecipeFilter.base_filters['is_in_shopping_cart'] = TypedChoiceFilter(
    choices=BOOLEAN_NUMBER_CHOICES,
    method='is_in_current_user_shopping_cart',
    coerce=int,
)
RecipeFilter.Meta.fields += ['is_in_shopping_cart']
RecipeFilter.is_in_current_user_shopping_cart = (
    is_in_current_user_shopping_cart
)
