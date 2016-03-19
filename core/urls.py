from django.conf.urls import url
from core import views


urlpatterns = [
    url(r'^$', views.index, name='site_index'),
    url(r'^products/$', views.products, name='products'),
    url(r'^products/all/$', views.products_all, name='products_all'),

    # shopping cart
    url(r'^cart/$', views.cart_view, name='cart'),
    url(r'^cart/update/$', views.update_cart, name='update_cart'),
    url(r'^cart/remove_all/$', views.remove_all, name='remove_all_from_cart'),
    url(r'^cart/add/(?P<product_id>[0-9]+)/$', views.add_to_cart, name='add_to_cart'),
    url(r'^cart/delete/(?P<cart_item>[0-9]+)/$', views.delete_from_cart, name='delete_from_cart'),

    # orders
    # url(r'^orders/$', views.products_all, name='orders'),
    url(r'^orders/create/$', views.create_order, name='create_order'),
    url(r'^feedback/$', views.create_feedback, name='create_feedback'),
]