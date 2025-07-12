from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .confirmation import get_confirmation_code, send_confirmation_code
from .models import CustomUser
from .serializers import TokenSerializer, SignupSerializer


class SignupView(APIView):
    """
    Регистрация нового пользователя.

    Права доступа: Доступно без токена.
    Использовать имя 'me' в качестве username запрещено (сериализатор).
    Поля email и username должны быть уникальными (представление).
    Должна быть возможность повторного запроса кода подтверждения.

    """
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_email = serializer.validated_data['email']
        validated_username = serializer.validated_data['username']

        try:
            user = CustomUser.objects.filter(
                Q(email=validated_email) | Q(username=validated_username)
            ).first()
            confirmation_code = get_confirmation_code()
            user.confirmation_code = confirmation_code
            user.save()
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.create_user(
                    username=validated_username,
                    email=validated_email,
                )
                confirmation_code = get_confirmation_code()
                user.confirmation_code = confirmation_code
                user.save()
            except IntegrityError:
                return Response(
                    {'error': 'Username or email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        send_confirmation_code(user.email, confirmation_code)

        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class TokenObtainView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            return Response(
                {'error': 'Неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.confirmation_code = None
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {'access': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
