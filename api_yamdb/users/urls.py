from django.urls import include, path
from rest_framework import routers

from .views import (
    MeView,
    SignupView,
    TokenObtainView,
    UserViewSet
)


router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')
router.register(r'<str:username>', UserViewSet, basename='user-detail')
router.register(r'me', MeView, basename='me')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
    path('', include(router.urls)),
]
