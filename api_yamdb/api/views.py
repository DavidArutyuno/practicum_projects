from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from api import serializers
from api.filter import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from reviews import models


User = get_user_model()


class SignupView(APIView):
    """
    Регистрация нового пользователя.
    Права доступа: Доступно без токена.
    """
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TokenObtainView(APIView):
    """
    Получение JWT-токена.

    Обрабатывает статус-коды:
    - 400: Некорректные данные (ошибки валидации)
    - 404: Пользователь не найден (определяется по code='not_found')
    - 200: Успешная выдача токена
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)

        if not serializer.is_valid():
            username_error = serializer.errors.get('username', [None])[0]
            error_code = getattr(username_error, 'code', None)

            status_code = (
                status.HTTP_404_NOT_FOUND if error_code == 'not_found'
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(serializer.errors, status=status_code)

        user = User.objects.get(username=serializer.validated_data['username'])

        refresh = RefreshToken.for_user(user)

        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями (только для администратора)."""
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return serializers.UserReadOrPatchSerializer
        if self.action in ('partial_update', 'update'):
            return serializers.UserReadOrPatchSerializer
        return serializers.UserSerializer

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        """Получение и изменение данных текущего пользователя."""
        user = request.user

        if request.method == 'PATCH':
            serializer = serializers.MeSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = serializers.MeSerializer(user)
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title с поддержкой CRUD и подсчётом рейтинга.
    """
    queryset = models.Title.objects.all().annotate(rating=Avg('review__score'))
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.TitleReadSerializer
        return serializers.TitleSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.TitleReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.TitleReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.TitleReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)


class BaseViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']


class CategoryViewSet(
    BaseViewSet,
):
    """
    ViewSet для модели Category.

    Операции:
        - GET: Получение списка категорий.
        - POST: Создание новой категории.
        - DELETE: Удаление категории по slug.

    Поиск:
        - По полю 'name'.
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(
    BaseViewSet,
):
    """
    ViewSet для модели Genre.

    Операции:
        - GET: Получение списка жанров.
        - POST: Создание нового жанра.
        - DELETE: Удаление жанра по slug.

    Поиск:
        - По полю 'name'.
    """
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review с поддержкой CRUD.
    """
    serializer_class = serializers.ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.ReviewReadSerializer
        return serializers.ReviewSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.ReviewReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.ReviewReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.ReviewReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return models.Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(models.Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Comment с поддержкой CRUD.
    """
    serializer_class = serializers.CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.CommentReadSerializer
        return serializers.CommentSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.CommentReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.CommentReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        instance = self.get_queryset().get(pk=response.data['id'])
        read_serializer = serializers.CommentReadSerializer(instance)
        return Response(read_serializer.data, status=response.status_code)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return models.Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(models.Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
