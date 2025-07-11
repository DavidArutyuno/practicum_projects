from django.urls import include, path
from rest_framework import routers

from api import views

API_VERSION = 'v1/'

router = routers.DefaultRouter()
router.register(r'titles', views.TitleViewSet, basename='titles')
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'genres', views.GenreViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path(API_VERSION, include(router.urls)),
]
