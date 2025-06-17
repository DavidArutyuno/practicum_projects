from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from api.views import (
    GroupList, GroupDetail, CommentViewSet, PostViewSet
)


router = routers.DefaultRouter()
router.register(
    r'api/v1/posts',
    PostViewSet,
    basename='posts'
)
router.register(
    r'api/v1/posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/groups/', GroupList.as_view()),
    path('api/v1/groups/<int:pk>/', GroupDetail.as_view()),
    path('api/v1/api-token-auth/', views.obtain_auth_token),
]
