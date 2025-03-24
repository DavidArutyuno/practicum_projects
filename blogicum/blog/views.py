from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.utils import timezone as dt

from blog.models import Post


now = dt.datetime.now()


def get_post(id=None, slug=None):
    if id:
        return get_object_or_404(Post.objects.select_related(
            'category', 'location', 'author').filter(
            pk=id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=now
        ))
    elif slug:
        return get_list_or_404(Post.objects.select_related(
            'category', 'location', 'author').filter(
            is_published=True,
            category__is_published=True,
            category__slug__exact=slug,
            pub_date__lte=now
        ))
    else:
        return Post.objects.select_related(
            'category', 'location', 'author').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now
        )[0:5]


def index(request):
    post_list = get_post()
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post_list = get_post(id=post_id)
    context = {'post': post_list}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    post_list = get_post(slug=category_slug)
    context = {
        'post_list': post_list,
        'category': post_list[0].category
    }
    return render(request, 'blog/category.html', context)
