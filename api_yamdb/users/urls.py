from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SignupView, TokenObtainView, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('', UserViewSet, basename='users')

auth_patterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token'),
]

urlpatterns = [
    path('auth/', include((auth_patterns, 'auth'))),

    path('', include(router.urls)),
]
