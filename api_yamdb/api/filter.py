from django_filters import rest_framework as filters

from reviews import models


class TitleFilter(filters.FilterSet):
    """
    Фильтрация по полям 'name', 'year', 'category__slug', 'genre__slug'.
    """
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = models.Title
        fields = ['name', 'year', 'category', 'genre']
