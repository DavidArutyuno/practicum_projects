from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

API_VERSION = 'v1/'

API_ROUTE = 'api/'
AUTH_ROUTE = API_ROUTE + API_VERSION + 'auth/'
USERS_ROUTE = API_ROUTE + API_VERSION + 'users/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path(API_ROUTE, include('api.urls')),
    path(AUTH_ROUTE, include('users.urls')),
    path(USERS_ROUTE, include('users.urls')),
]
