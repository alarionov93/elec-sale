from io import StringIO
import random
from django.core import serializers
import json

from django.core.serializers.json import Serializer
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from core import models
from elec_site import settings
from django.forms.models import model_to_dict

class JSONSerializer(Serializer):

    fields = []

    def __init__(self, fields=fields):
        super(JSONSerializer, self).__init__()
        self.fields = fields

    def serialize(self, queryset, **options):
        self.options = options
        self.stream = options.get("stream", StringIO())
        self.start_serialization()
        self.use_natural_primary_keys = True
        self.first = True

        for obj in queryset:
            self.start_object(obj)
            for field in self.fields:
                self.handle_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()

        return self.getvalue()

    def handle_field(self, obj, field):
        self._current[field] = getattr(obj, field)


# TODO: rewrite this shit using extending and django CBV !!

def index(request):
    limit_val = 3
    products = models.Product.objects.filter(in_stock=1).order_by('?')[:limit_val]
    products_all_count = models.Product.objects.filter(in_stock=1).count()
    ctx = {
        'products': products,
        'images_dir': settings.MEDIA_URL,
        'at_page': limit_val,
        'products_all_count': products_all_count,
    }

    return render(request, 'product-tile.html', ctx)


def products(request):
    if request.is_ajax():
        limit_val = 3
        products = models.Product.objects.filter(in_stock=1).order_by('?')[:limit_val]
        products_all_count = models.Product.objects.filter(in_stock=1).count()

        serializer = JSONSerializer(fields=['id', 'name', 'cost', 'in_stock', 'thumbs', 'images'])
        json_model = serializer.serialize(queryset=products)

        ctx = {
            'products': json_model,
            'images_dir': settings.MEDIA_URL,
            'at_page': limit_val,
            'products_all_count': products_all_count,
        }

        return JsonResponse(ctx)
    else:
        raise Http404('Not found')


def products_all(request):
    if request.is_ajax():
        products = models.Product.objects.filter(in_stock=1).all()

        serializer = JSONSerializer(fields=['id', 'name', 'cost', 'in_stock', 'thumbs', 'images'])
        json_model = serializer.serialize(queryset=products)

        ctx = {
            'products': json_model,
            'images_dir': settings.MEDIA_URL,
        }

        return JsonResponse(ctx)
    else:
        raise Http404('Not found')