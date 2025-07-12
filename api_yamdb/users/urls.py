from django.urls import path
from .views import (
    SignupView, TokenObtainView
)

TOKEN = 'token/'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
]
