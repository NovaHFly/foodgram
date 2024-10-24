import django_filters

from .models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ['name']
