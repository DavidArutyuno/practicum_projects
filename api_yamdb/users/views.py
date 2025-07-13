from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser
)

from .confirmation import get_confirmation_code, send_confirmation_code
from .permissions import IsAdmin
from .serializers import (
    SignupSerializer,
    TokenSerializer,
    UserSerializer,
    UserReadOrPatchSerializer,
    MeSerializer
)


User = get_user_model()


class SignupView(APIView):
    """
    Регистрация нового пользователя.

    Права доступа: Доступно без токена.
    Использовать имя 'me' в качестве username запрещено (сериализатор).
    Поля email и username должны быть уникальными (представление).
    Должна быть возможность повторного запроса кода подтверждения.

    """
    throttle_classes = (AnonRateThrottle,)
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        try:
            user = User.objects.filter(
                Q(email=email) & Q(username=username)).first()

            if user:
                user.email = email
            else:
                user = User(email=email, username=username)

            user.confirmation_code = get_confirmation_code()
            user.save()

            send_confirmation_code(user.email, user.confirmation_code)

            return Response({
                'email': user.email,
                'username': user.username
            }, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenObtainView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
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


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями (только для администратора)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return UserReadOrPatchSerializer
        if self.action in ('partial_update', 'update'):
            return UserReadOrPatchSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        """Получение и изменение данных текущего пользователя."""
        user = request.user
        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = MeSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
