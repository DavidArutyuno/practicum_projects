from django.urls import include, path
from rest_framework import routers

from api import views

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('genres', views.GenreViewSet, basename='genres')
router.register('titles', views.TitleViewSet, basename='titles')

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

auth_patterns = [
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/token/', views.TokenObtainView.as_view(), name='token'),
]

urlpatterns = [
    *auth_patterns,
    path('', include(router.urls)),
]
