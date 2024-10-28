import django_filters

from .models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(lookup_expr='id')
    is_favorited = django_filters.ChoiceFilter(
        choices=[[0, False], [1, True]], method='favorited_by_current_user'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[[0, False], [1, True]], method='in_current_user_shopping_cart'
    )
    tags = django_filters.CharFilter(method='filter_tags', distinct=True)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

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

    def filter_tags(self, queryset, name, value):
        arg_list = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=arg_list)
