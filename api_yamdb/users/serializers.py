from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator


User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Сериализация данных пользователя в процессе регистрации."""
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email - обязательное поле.")
        return value.lower()


class TokenSerializer(serializers.Serializer):
    """Сериализация данных пользователя в процессе получения токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализация данных в процессе создания и обновления
    пользователя администратором.
    """
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value


class UserReadOrPatchSerializer(serializers.ModelSerializer):
    """
    Сериализация данных для процесса чтения и
    частичного обновления профиля пользователя.
    """
    username = serializers.CharField(
        required=False,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=False,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(
        choices=settings.ROLE_CHOICES,
        required=False,
        error_messages={
            'invalid_choice': 'Неверная роль.'
            'Допустимые значения: user, moderator, admin'
        }
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value


class MeSerializer(serializers.ModelSerializer):
    """Сериализация данных для работы с собственным профилем."""
    username = serializers.CharField(
        required=False,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.'
            )
        ]
    )
    email = serializers.EmailField(
        required=False,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать "me" в качестве username запрещено'
            )
        return value
