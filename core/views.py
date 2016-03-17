from django.contrib.auth.decorators import login_required
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

# Cart

def add_to_cart(request, product_id):
    prod_ids = []
    cart = request.session.get('cart', None)
    status = 0
    if cart is not None:
        d_cart = json.loads(cart)
        prod_ids = d_cart # this line is here for sure that the deal is with list
    else:
        request.session['cart'] = ""
    prod_ids.append(product_id)
    s_cart = json.dumps(prod_ids)
    request.session['cart'] = s_cart
    # TODO: change status if something gone wrong
    status = json.dumps({'status': status})

    return HttpResponse(status, content_type='application/json')


def update_cart(request):
    cart = request.session.get('cart', None)
    d_cart = []
    products = []
    if cart is not None:
        d_cart = json.loads(cart)
    #     for val in d_cart:
    #         p = models.Product.objects.get(pk=val)
    #         products.append(p)
    # s_cart = serializers.serialize('json', products, use_natural_foreign_keys=True, use_natural_primary_keys=True)


    return HttpResponse(cart, content_type='application/json')


def cart_view(request):

    return render(request, 'cart.html')


def delete_from_cart(request, cart_item):
    prod_ids = []
    cart = request.session.get('cart', None)
    status = 0
    if cart is not None:
        d_cart = json.loads(cart)
        prod_ids = d_cart # TODO: is this line necessary? then we exactly know that type of prod_ids is list, not other!
        try:
            item_to_delete = prod_ids.pop(int(cart_item))
        except KeyError:
            status = 1
            raise Http404("Sorry, but index is out of range.")
        except:
            status = 2
            raise Http404("Unhandled exception.")
        s_cart = json.dumps(prod_ids)
        if len(prod_ids) == 0:
            del request.session['cart']
        else:
            request.session['cart'] = s_cart

    else:
        request.session['cart'] = ""
    status = json.dumps({'status': status})

    return HttpResponse(status, content_type='application/json')


def remove_all(request):
    cart = request.session.get('cart', None)
    # TODO: change with try-except here!!
    status = 0
    if cart is not None:
        del request.session['cart']
    else:
        status = 1
    status = json.dumps({'status': status})

    return HttpResponse(status, content_type='application/json')