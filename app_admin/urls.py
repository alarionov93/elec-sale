from django.conf.urls import url
from app_admin import views

urlpatterns = [
    url(r'^$', views.AdminIndex.as_view(), name='admin_index'),
    url(r'^login/$', views.admin_login, name='login'),
    url(r'^logout/$', views.admin_logout, name='logout'),

    # products
    url(r'^products/$', views.ProductsList.as_view(), name='products_list'),
    url(r'^products/add/$', views.ProductCreate.as_view(), name='product_add'),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductUpdate.as_view(), name='product_update'),
]