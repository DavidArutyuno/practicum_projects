from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

API_ROUTE = 'api/'
AUTH_ROUTE = API_ROUTE + 'v1/auth/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path(API_ROUTE, include('api.urls')),
    path(AUTH_ROUTE, include('users.urls')),
]
