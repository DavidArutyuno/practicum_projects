from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Информация о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user,
                author=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Регистрация пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создается новый объект в БД."""
        return User.objects.create_user(**validated_data)


class SetAvatarSerializer(serializers.ModelSerializer):
    """Добавление аватара текущего пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SetPasswordSerializer(serializers.ModelSerializer):
    """Изменение пароля текущего пользователя."""

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate_current_password(self, value):
        """Проверяем пароль при запросе обновления пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value


class TagSerializer(serializers.ModelSerializer):
    """Список тегов и получение тега по id."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиенты в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Минимальный набор данных для превью рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализация данных для GET запросов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_list',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def _check_object_exists(self, obj, model_class):
        """Универсальный метод для проверки существования связи
        между пользователем и рецептом."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return model_class.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def get_is_favorited(self, obj):
        return self._check_object_exists(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._check_object_exists(obj, ShoppingCart)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализация данных для запросов изменяющих данные."""

    image = Base64ImageField()
    ingredients = serializers.JSONField()
    tags = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        extra_kwargs = {
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
        }

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
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

    def validate_tags(self, value):
        """Валидация тегов."""
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым'
            )

        existing_count = Tag.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError('Указаны несуществующие теги')
        return value

    def _create_ingredient_relations(self, recipe, ingredients_data):
        """
        Массовое создание связей ингредиентов с рецептом через bulk_create.
        """
        ingredient_objects = []

        for ingredient_data in ingredients_data:
            ingredient_objects.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient_data['id'],
                    amount=ingredient_data['amount']
                )
            )

        IngredientInRecipe.objects.bulk_create(
            ingredient_objects, batch_size=settings.BATCH_SIZE
        )

    def create(self, validated_data):
        """Используем bulk_create для оптимизации."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        self._create_ingredient_relations(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        instance.tags.set(tags_data)

        instance.ingredient_list.all().delete()
        self._create_ingredient_relations(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class UserWithRecipesSerializer(UserSerializer):
    """Подписки пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return RecipeMiniSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
