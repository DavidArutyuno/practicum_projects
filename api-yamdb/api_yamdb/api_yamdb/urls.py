from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

API_VERSION = 'v1'
API_PREFIX = f'api/{API_VERSION}/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path(f'{API_PREFIX}', include('api.urls')),
]
