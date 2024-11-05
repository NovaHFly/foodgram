from django.db.models import QuerySet
from django_filters import TypedChoiceFilter

from common.const import BOOLEAN_NUMBER_CHOICES
from recipes.filters import RecipeFilter


def favorited_by_current_user(
    self,
    queryset: QuerySet,
    name: str,
    value: int,
) -> QuerySet:
    if self.request.user.is_anonymous:
        return queryset.none()

    lookup_params = {'favorites_lists__user__in': [self.request.user]}
    if not value:
        return queryset.exclude(**lookup_params)
    return queryset.filter(**lookup_params)


RecipeFilter.base_filters['is_favorited'] = TypedChoiceFilter(
    choices=BOOLEAN_NUMBER_CHOICES,
    method='favorited_by_current_user',
    coerce=int,
)
RecipeFilter.Meta.fields += ['is_favorited']
RecipeFilter.favorited_by_current_user = favorited_by_current_user
