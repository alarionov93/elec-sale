from django.shortcuts import render
from core import models


def index(request):
    products = models.Product.objects.all()
    ctx = {
        'products': products
    }

    return render(request, 'product-tile.html', ctx)

