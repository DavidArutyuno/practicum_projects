from django.db.models import Count
from django.utils import timezone as dt

from blog.models import Post


def get_posts():
    """Выборка всех постов."""
    return Post.objects.select_related(
        'category', 'location', 'author',
    ).annotate(
        comment_count=Count('post_comments')
    ).order_by('-pub_date')


def get_filter_queryset(queryset):
    """Выборка постов по основным критериям."""
    now = dt.datetime.now()
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now
    )
