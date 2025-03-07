from django.shortcuts import render

# Create your views here.


def about(request):
    template = 'pages/about.html'
    context = dict()
    return render(request, template, context)


def rules(request):
    template = 'pages/rules.html'
    context = dict()
    return render(request, template, context)
