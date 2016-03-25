import random
import uuid
import json
from collections import Counter

from core.mails import mail_body
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, render_to_response
from core import models
from django.template import Template, Context
from django.utils import timezone
from django.utils.timezone import localtime
from elec_site import settings
from core.json_serializer import JSONSerializer

# TODO: rewrite this shit using extending and django CBV !!

def index(request):
    limit_val = 3
    products = models.Product.objects.filter(left_in_stock__gte=1).order_by('?')[:limit_val]
    products_all_count = models.Product.objects.filter(left_in_stock__gte=1).count()
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
        products = models.Product.objects.filter(left_in_stock__gte=1).order_by('?')[:limit_val]
        products_all_count = models.Product.objects.filter(left_in_stock__gte=1).count()

        serializer = JSONSerializer(fields=['id', 'name', 'cost', 'left_in_stock', 'in_stock', 'thumbs', 'images'])
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
        products = models.Product.objects.all()

        serializer = JSONSerializer(fields=['id', 'name', 'desc', 'cost', 'left_in_stock', 'in_stock', 'thumbs', 'images'])
        json_model = serializer.serialize(queryset=products)

        ctx = {
            'products': json_model,
            'images_dir': settings.MEDIA_URL,
        }

        return JsonResponse(ctx)
    else:
        raise Http404('Not found')


def product(request, product_id):
    product_id = int(product_id)
    product = models.Product.objects.get(pk=product_id)
    ctx = {
        'product': product,
        'images_dir': settings.MEDIA_URL,
        'thumbs': product.thumb_urls,
        'images': product.images,
    }

    return render(request, 'product-view.html', ctx)

# Cart

def add_to_cart(request, product_id):
    # del request.session['cart']
    prod_data = []
    cart = request.session.get('cart', None)
    product_id = int(product_id)
    status = 0
    found = 0
    if cart is not None:
        d_cart = json.loads(cart)
        prod_data = d_cart # this line is here for sure that the deal is with list
    else:
        request.session['cart'] = ""
    for p in prod_data:
        if p['id'] == product_id:
            p['count'] = p['count'] + 1
            found = 1
    if not found:
        prod_data.append({'id': product_id, 'count': 1})

    s_cart = json.dumps(prod_data)
    request.session['cart'] = s_cart

    # products = []
    # for p in prod_data:
    #         product = models.Product.objects.get(pk=p['id'])
    #         setattr(product, 'count', p['count'])
    #         products.append(product)
    # serializer = JSONSerializer(fields=['id', 'name', 'cost', 'in_stock', 'thumbs', 'images', 'count'])
    # cart = serializer.serialize(queryset=products)
    status = json.dumps({'status': status, 'cart': prod_data})

    return HttpResponse(status, content_type='application/json')


def update_cart(request):
    cart = request.session.get('cart', None)
    status = 0
    d_cart = []
    if cart is not None:
        d_cart = json.loads(cart)

    status = json.dumps({'status': status, 'cart': d_cart})

    return HttpResponse(status, content_type='application/json')


def cart_view(request):

    return render(request, 'cart.html')

# TODO: define view to decrease/increase product count

def delete_from_cart(request, product_id):
    prod_data = []
    cart = request.session.get('cart', None)
    product_id = int(product_id)
    status = 0
    if cart is not None:
        d_cart = json.loads(cart)
        prod_data = d_cart # TODO: is this line necessary? then we exactly know that type of prod_ids is list, not other!
        try:
            deleted = None
            for i,p in enumerate(prod_data):
                if p['id'] == product_id:
                    deleted = prod_data.pop(i)
            if deleted is None:
                status = 3
        except KeyError:
            status = 1
            raise Http404("Sorry, but index is out of range.")
        except:
            status = 2
            raise Http404("Unhandled exception.")
        if len(prod_data) == 0:
            del request.session['cart']
        else:
            request.session['cart'] = json.dumps(prod_data)
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
    ip = request.environ.get('REMOTE_ADDR', None)
    if request.is_ajax() and request.method == 'POST':
        cart = request.session.get('cart', None)
        email = request.POST.get('email', None)
        phone = request.POST.get('phone', None)
        total = request.POST.get('total', None)
        ctx = {}
        if cart is not None and email and phone and total:
            try:
                order_number = str(uuid.uuid1())[:8]
                order = models.Order(number=order_number, user_phone=phone, user_email=email, total=total)
                order_items_list = json.loads(cart)
                order.save()
                for val in order_items_list:
                    prod = models.Product.objects.get(pk=val['id'])
                    item = models.OrderItem(product=prod, order=order, count=val['count'])
                    item.save()
                    order.orderitem_set.add(item)
                    decrease = prod.left_in_stock - int(val['count'])
                    prod.left_in_stock = decrease
                    prod.save()
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
            status = send_mail('Ваш заказ в магазине электроники elec-all.ru', body, settings.ADMIN_EMAIL,
                    [email], fail_silently=settings.MAIL_FAIL_SILENT, auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD, html_message=body)
            body += ';\r\n IP is [%s]' % ip
            status2 = send_mail('Новый заказ!', body, settings.ADMIN_EMAIL,
                    [settings.ADMIN_EMAIL], fail_silently=settings.MAIL_FAIL_SILENT, auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD, html_message=body)

            ctx.update({'customer_stat': status, 'admin_stat': status2})
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


def create_feedback(request):
    # del request.session['voted']
    voted = request.session.get('voted', None)
    ip = request.environ.get('REMOTE_ADDR', None)
    if voted is not None:
        if (int(timezone.now().timestamp()) - int(voted)) > 86400:
            del request.session['voted']
    if request.is_ajax() and request.method == 'POST' and not voted:
        email = request.POST.get('email', None)
        feedback = request.POST.get('feedback', None)
        if email and feedback:
            try:
                body = "%s wrote feedback on \'elec-all.ru\': ``%s``; IP is [%s]" % (email, ip, feedback)
                status = send_mail('Feedback from elec-all.ru', body, settings.ADMIN_EMAIL,
                    [settings.ADMIN_EMAIL], fail_silently=settings.MAIL_FAIL_SILENT, auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD)
                ctx = {'mail_stat': status}
            except:
                raise Http404("Unhandled exception.")

            ctx.update({
                'status': 0,
                'error': None,
                'success': 'Вы успешно отправили отзыв, спасибо!'
            })

            request.session['voted'] = int(timezone.now().timestamp())
        else:
            ctx = {
                'status': 1,
                'error': 'email OR feedback is None',
                'success': None
            }
    elif voted:
        ctx = {
            'status': 3,
            'success': 'Спасибо, вы уже написали отзыв!',
            'error': 'voted already',
        }
    else:
        ctx = {
            'status': 2,
            'error': 'only ajax POST allowed',
            'success': None
        }

    return HttpResponse(json.dumps(ctx), content_type='application/json')


def create_purchase(request):
    if request.is_ajax() and request.method == 'POST':
        email = request.POST.get('email', None)
        purchase = request.POST.get('purchase', None)
        ip = request.environ.get('REMOTE_ADDR', None)
        if email and purchase:
            try:
                body = "%s wrote purchase on \'elec-all.ru\'. IP is: [%s] He wants to know about: ``%s``" % (email, ip, purchase)
                status = send_mail('Purchase on elec-all.ru', body, settings.ADMIN_EMAIL,
                    [settings.ADMIN_EMAIL], fail_silently=settings.MAIL_FAIL_SILENT, auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD)
                ctx = {'mail_stat': status}
            except:
                raise Http404("Unhandled exception.")

            ctx.update({
                'status': 0,
                'error': None,
                'success': 'Спасибо за интерес к нашей компании! Мы свяжемся с вами, как только получим информацию о интересующей вас позиции!'
            })
        else:
            ctx = {
                'status': 1,
                'error': 'email OR feedback is None',
                'success': None
            }
    else:
        ctx = {
            'status': 2,
            'error': 'only ajax POST allowed',
            'success': None
        }

    return HttpResponse(json.dumps(ctx), content_type='application/json')