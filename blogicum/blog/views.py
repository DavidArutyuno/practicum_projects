from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import (
    get_object_or_404, get_list_or_404, render, redirect
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone as dt
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Comment, Post, User
from blog.utils import get_posts, get_filter_queryset
from blogicum import settings as s

from .form import PostForm, UserForm, CommentForm


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    queryset = get_posts()


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


# Главная страница
class PostListView(PostMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = s.PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        return get_filter_queryset(queryset)


# ПОСТЫ ПОЛЬЗОВАТЕЛЯ В ПРОФИЛЕ:
class ProfilePostListView(PostMixin, ListView):
    paginate_by = s.PAGINATE_BY
    template_name = 'blog/profile.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        # context['page_obj'] = (
        #     self.get_queryset()
        # )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserForm(
                self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserForm(instance=self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


# Катогории
class CategoryListView(PostMixin, ListView):
    template_name = 'blog/category.html'
    paginate_by = s.PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        return get_filter_queryset(queryset).filter(
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)
        return context


# ПОСТЫ:
class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
            # kwargs={'username': self.request.user}
        )


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        post_detail_queryset = get_filter_queryset(queryset)
        if self.request.user.is_authenticated:
            # Если пользователь авторизован, то ему доступны
            # все его записи
            return post_detail_queryset | queryset.filter(
                author=self.request.user)
        # Для пользователя без авторизации возвращаем
        # QuerySet с базовой фильтрацией
        return post_detail_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.select_related().filter(
            post_id=self.kwargs['post_id']
        )
        return context


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_queryset(self):
        queryset = get_posts()
        return queryset.filter(pk=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):
    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})

    # from django.contrib.auth.mixins import LoginRequiredMixin
    # from django.views.generic import TemplateView

    # class MyProtectedView(LoginRequiredMixin, TemplateView):
    #     template_name = "my_template.html"
    #     login_url = "/login/"  # куда перенаправить неавторизованных


# КОММЕНТАРИИ
class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_object
        return context


class CommentDetailView(DetailView):
    model = Comment
    template_name = 'blog/comments.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
