from django.utils import timezone as dt

from blog.models import Post


def get_posts(slug=None):
    now = dt.datetime.now()
    return Post.objects.select_related(
        'category', 'location', 'author').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now
    )
