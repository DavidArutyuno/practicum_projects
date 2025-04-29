from django.conf import settings as s
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Comment, Post, User
from blog.utils import get_posts, get_filter_queryset
from blog.mixins import (
    OnlyAuthorMixin, CommentMixin, PostMixin, GetSuccessUrlPostDetailMixin,
    GetSuccessUrlProfileMixin
)
from .form import PostForm, UserForm, CommentForm


class PostListView(PostMixin, ListView):
    """Главная страница."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = s.PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        return get_filter_queryset(queryset)


class ProfilePostListView(PostMixin, ListView):
    """Посты пользователя в профиле."""

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
        return context


class ProfileUpdateView(
    LoginRequiredMixin, GetSuccessUrlProfileMixin, UpdateView
):
    """Редактирование профиля пользователя."""

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


class CategoryListView(PostMixin, ListView):
    """Список тематических постов."""

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


class PostCreateView(
    LoginRequiredMixin, PostMixin, GetSuccessUrlProfileMixin, CreateView
):
    """Создание поста."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_published = True
        return super().form_valid(form)


class PostDetailView(PostMixin, DetailView):
    """
    Просмотр конкретного поста.

    def get_queryset:
        Если пользователь авторизован, то ему доступны все его записи.
        Иначе возвращаем QuerySet с базовой фильтрацией.
    """

    template_name = 'blog/detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        post_detail_queryset = get_filter_queryset(queryset)
        if self.request.user.is_authenticated:
            return post_detail_queryset | queryset.filter(
                author=self.request.user)
        return post_detail_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = (
            Comment.objects.select_related('post', 'author',
                                           ).filter(
                                               post_id=self.kwargs['post_id'])
        )
        return context


class PostDeleteView(OnlyAuthorMixin, GetSuccessUrlProfileMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_queryset(self):
        queryset = get_posts()
        return queryset.filter(pk=self.kwargs['post_id'])


class PostUpdateView(
    OnlyAuthorMixin, PostMixin, GetSuccessUrlPostDetailMixin, UpdateView
):
    """Редактирование поста."""

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CommentCreateView(
    LoginRequiredMixin, CommentMixin, GetSuccessUrlPostDetailMixin, CreateView
):
    """Создание комментария к посту."""

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_object
        return context


class CommentDeleteView(
    OnlyAuthorMixin, GetSuccessUrlPostDetailMixin, DeleteView
):
    """Удаление комментария к посту."""

    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(pk=self.kwargs['comment_id'])


class CommentUpdateView(
    OnlyAuthorMixin, CommentMixin, GetSuccessUrlPostDetailMixin, UpdateView
):
    """Редактирование комментария к посту."""
