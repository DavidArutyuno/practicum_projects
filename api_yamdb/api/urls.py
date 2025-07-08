from django.urls import include, path
from rest_framework import routers

from api import views

API_VERSION = 'v1/'

router = routers.DefaultRouter()
router.register(r'titles', views.TitleViewSet, basename='titles')
router.register(r'categories', views.CategoryViewSet, basename='categories')

urlpatterns = [
    path(API_VERSION, include(router.urls)),
]
