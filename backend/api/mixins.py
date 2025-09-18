from rest_framework import serializers

from recipes.models import Ingredient, Tag


class IngredientsValidationMixin:
    """Миксин для проверки ингредиентов."""

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым'
            )

        ingredient_ids = [item['id'] for item in value]
        existing_count = Ingredient.objects.filter(
            id__in=ingredient_ids).count()

        if existing_count != len(ingredient_ids):
            raise serializers.ValidationError(
                'Указаны несуществующие ингредиенты'
            )

        for ingredient_data in value:
            amount = ingredient_data.get('amount')
            if amount is None:
                raise serializers.ValidationError(
                    'Для каждого ингредиента должно быть указано количество'
                )

            try:
                amount_int = int(amount)
                if amount_int < 1:
                    raise serializers.ValidationError(
                        'Количество ингредиента должно быть не менее 1'
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    'Количество должно быть числом'
                )

        return value


class TagsValidationMixin:
    """Миксин для проверки тегов."""

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым'
            )

        existing_count = Tag.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError('Указаны несуществующие теги')
        return value


class PasswordValidationMixin:
    """Миксин для проверки пароля."""

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value
