from django.urls import include, path
from rest_framework import routers

from api.views import (
    GroupViewSet, CommentViewSet, PostViewSet, FollowViewSet
)

API_VERSION_1 = 'v1/'

router = routers.DefaultRouter()
router.register(
    r'groups',
    GroupViewSet,
    basename='groups'
)

router.register(
    r'follow',
    FollowViewSet,
    basename='follow'
)

router.register(
    r'posts',
    PostViewSet,
    basename='posts'
)
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path(API_VERSION_1, include(router.urls)),
    path(API_VERSION_1, include('djoser.urls')),
    path(API_VERSION_1, include('djoser.urls.jwt')),
]
