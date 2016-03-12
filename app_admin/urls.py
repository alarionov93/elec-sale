from django.conf.urls import url
from app_admin import views

urlpatterns = [
    url(r'^$', views.AdminIndex.as_view(), name='admin_index'),
    url(r'^login/$', views.admin_login, name='login'),
    url(r'^logout/$', views.admin_logout, name='logout'),
]