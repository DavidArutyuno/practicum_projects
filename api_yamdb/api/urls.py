from django.urls import include, path
from rest_framework import routers

from api import views

API_VERSION = 'v1/'

router = routers.DefaultRouter()
router.register(r'titles', views.TitleViewSet, basename='titles')

urlpatterns = [
    path(API_VERSION, include(router.urls)),
]
