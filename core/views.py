from django.shortcuts import render


def index(request):
    ctx = {}

    return render(request, 'index.html', ctx)

def products(request):
    ctx = {}

    return render(request, 'product-tile.html', ctx)

