from django.conf.urls import url
from core import views


urlpatterns = [
    url(r'^$', views.index, name='site_index'),
    url(r'^products/$', views.products, name='products'),
    url(r'^products/all/$', views.products_all, name='products_all'),
]