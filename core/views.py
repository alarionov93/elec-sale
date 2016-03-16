import random
from django.shortcuts import render
from core import models
from elec_site import settings


def index(request):
    products = models.Product.objects.filter(in_stock=1).order_by('?')
    ctx = {
        'products': products,
        'images_dir': settings.MEDIA_URL,
        'max_at_page': 3,
        'products_count': len(products),
    }

    return render(request, 'product-tile.html', ctx)

