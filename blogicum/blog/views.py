from datetime import datetime as dt

from blog.models import Post

from django.shortcuts import get_object_or_404, get_list_or_404, render


def index(request):
    post_list = Post.objects.select_related('category', 'location', 'author').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=dt.now()
    )[0:5]

    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post_list = get_object_or_404(Post.objects.select_related(
        'category', 'location', 'author').filter(
        pk=post_id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=dt.now()
    ))
    context = {'post': post_list}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    post_list = get_list_or_404(Post.objects.select_related(
        'category', 'location', 'author').filter(
        is_published=True,
        category__is_published=True,
        category__slug__exact=category_slug,
        pub_date__lte=dt.now()
    ))

    context = {
        'post_list': post_list,
        'category': post_list[0].category
    }
    return render(request, 'blog/category.html', context)
