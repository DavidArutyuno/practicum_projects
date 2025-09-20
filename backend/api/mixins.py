from rest_framework import status
from rest_framework.response import Response

from .serializers import RecipeMiniSerializer


class FavoriteShoppingCartMixin:
    """Миксин для обработки избранного и корзины покупок."""

    def _handle_favorite_shopping_cart(
            self, request, pk, model_class, messages):
        """
        Универсальный обработчик для избранного и корзины.

        Аргументы метода:
            request: HTTP запрос
            pk: ID рецепта
            model_class: класс модели (Favorite или ShoppingCart)
            messages: словарь с сообщениями {'post_error', 'delete_error'}
        """
        recipe = self.get_object()

        if request.method == 'POST':
            obj, created = model_class.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'error': messages['post_error']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RecipeMiniSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            try:
                obj = model_class.objects.get(
                    user=request.user,
                    recipe=recipe
                )
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except model_class.DoesNotExist:
                return Response(
                    {'error': messages['delete_error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
