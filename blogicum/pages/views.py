from django.shortcuts import render

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView


@login_required
def user_logout(request):
    logout(request)
    return render(request, 'registration/logged_out.html')


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_failure(request, reason=''):
    return render(request, 'pages/500.html', status=500)
