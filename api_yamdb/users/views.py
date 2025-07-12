from django.db import IntegrityError
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser
)

from .confirmation import get_confirmation_code, send_confirmation_code
from .models import CustomUser
from .permissions import IsAdmin, IsAdminOrSelf, IsUser
from .serializers import (
    SignupSerializer, TokenSerializer,
    UserSerializer, UserReadOrPatchSerializer
)


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
            user = CustomUser.objects.filter(
                Q(email=email) & Q(username=username)).first()

            if user:
                user.email = email
            else:
                user = CustomUser(email=email, username=username)

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset

    def get_serializer_class(self):
        if self.action in ('partial_update', 'retrieve'):
            return UserReadOrPatchSerializer
        return super().get_serializer_class()


class MeView(viewsets.ViewSet):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (IsUser,)
    http_method_names = ['get', 'patch']

    def retrieve(self, request):
        serializer = UserReadOrPatchSerializer(request.user)
        return Response(serializer.data)

    def partial_update(self, request):
        serializer = UserReadOrPatchSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
