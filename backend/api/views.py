from io import BytesIO

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters import rest_framework as filters
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.pagination import StandardResultsSetPagination
from core.utils import generate_short_hash
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeListSerializer, RecipeMiniSerializer,
                          SetAvatarSerializer, SetPasswordSerializer,
                          TagSerializer, UserCreateSerializer, UserSerializer,
                          UserWithRecipesSerializer)


def redirect_short_link(request, short_hash):
    """Перенаправление по короткой ссылке на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_hash)

    return redirect(f'/recipes/{recipe.id}')


class UserViewSet(viewsets.ModelViewSet):
    """
    Описание:

    - динамический выбор сериализатора (регистрация и остальные действия)
    - динамические разрешения (permissions)
    - получение данных текущего пользователя (me)
    - добавление аватара текущего пользователя (set_avatar)
    - удаление аватара текущего пользователя (delete_avatar)
    - изменение пароля текущего пользователя (set_password)
    - подписка на пользователя
    - отписка от пользователя
    """

    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['delete', 'put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def me_avatar(self, request):
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                request.user, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Мои подписки."""
        users = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(users)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )
            if not created:
                return Response(
                    {'error': 'Уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted = Subscription.objects.filter(
                user=request.user,
                author=author
            ).delete()[0]
            if not deleted:
                return Response(
                    {'error': 'Не были подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Метод не разрешен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов и получение тега по id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список ингредиентов с возможностью поиска по имени."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Рецепты.

    Список рецептов
    - Страница доступна всем пользователям.
    - Доступна фильтрация по избранному, автору, списку покупок и тегам.
    """

    queryset = Recipe.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_link']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in (
                ['favorite', 'shopping_cart', 'download_shopping_cart']):
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            # Добавление в избранное
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeMiniSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            # Удаление из избранного
            deleted = Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()[0]
            if not deleted:
                return Response(
                    {'error': 'Рецепта не было в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Метод не разрешен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            # Добавление в корзину покупок
            cart_item, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'error': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeMiniSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            # Удаление из корзины покупок
            deleted = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()[0]
            if not deleted:
                return Response(
                    {'error': 'Рецепта не было в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Метод не разрешен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=True,
        url_path='get-link',
        methods=['get']
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_id = generate_short_hash(recipe.id)
        short_link = f'{request.build_absolute_uri("/")}s/{short_id}'
        return Response({'short-link': short_link})

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        format = request.query_params.get('format', 'txt')

        if format == 'pdf':
            return self._generate_pdf_shopping_list(ingredients)
        else:
            return self._generate_text_shopping_list(ingredients)

    def _generate_text_shopping_list(self, ingredients):
        content = "Список покупок:\n\n"
        for item in ingredients:
            content += (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def _generate_pdf_shopping_list(self, ingredients):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        p.drawString(100, 800, "Список покупок:")
        y = 780
        for item in ingredients:
            if y < 100:
                p.showPage()
                y = 800
            text = (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}"
            )
            p.drawString(100, y, text)
            y -= 20

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        return response
