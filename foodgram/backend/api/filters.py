from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтры по тегам, избранному и корзине."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_tags(self, queryset, name, value):
        if value:
            queryset = queryset.filter(tags__slug__in=value).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset
