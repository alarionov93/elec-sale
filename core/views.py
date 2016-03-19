import uuid
import json

from core.mails import mail_body
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, render_to_response
from core import models
from django.template import Template, Context
from elec_site import settings
from core.json_serializer import JSONSerializer

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

    return render(request, 'product-tiles.html', ctx)


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
    products = []
    if cart is not None:
        d_cart = json.loads(cart)
        for val in d_cart:
            p = models.Product.objects.get(pk=val)
            products.append(p)
    serializer = JSONSerializer(fields=['id', 'name', 'cost', 'in_stock', 'thumbs', 'images'])
    cart = serializer.serialize(queryset=products)

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

# TODO: product.count-- in create_order !!
def create_order(request):
    if request.is_ajax() and request.method == 'POST':
        cart = request.session.get('cart', None)
        email = request.POST.get('email', None)
        phone = request.POST.get('phone', None)
        total = request.POST.get('total', None)
        ctx = {}
        if cart is not None and email and phone and total:
            try:
                order_number = str(uuid.uuid1())
                order = models.Order(number=order_number, user_phone=phone, user_email=email, total=total)
                order_items_list = json.loads(cart)
                order.save()
                for val in order_items_list:
                    prod = models.Product.objects.get(pk=val)
                    item = models.OrderItem(product=prod, order=order)
                    item.save()
                    order.orderitem_set.add(item)
                order.save()
                del request.session['cart']
            # TODO: catch all possible exceptions here!!
            except IntegrityError:
                raise Http404("Sorry, value of key is duplicated!")
            except:
                raise Http404("Unhandled exception.")

            ctx = {
                'status': 0,
                'order': order.to_json(),
                'error': None,
                'success': 'Ваш заказ принят, спасибо!'
            }
            body = mail_body(ctx)
            # TODO: send one more email: for me to know about new order
            # TODO: surround with try-except!!!!
            status = send_mail('Ваш заказ в магазине электроники elec-all.ru', body, 'alarionov93@yandex.ru',
                    ['alarionov93@yandex.ru'], fail_silently=settings.MAIL_FAIL_SILENT, auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD, html_message=body)
            ctx.update({'mail_stat': status})
        else:
            ctx = {
                'status': 1,
                'error': 'cart OR email OR phone is None',
            }
    else:
        ctx = {
            'status': 2,
            'error': 'only ajax POST allowed',
        }

    return HttpResponse(json.dumps(ctx), content_type='application/json')