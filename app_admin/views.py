import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin, View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, DetailView
from core import models
from bootstrap3.templatetags.bootstrap3 import bootstrap_field
from app_admin.forms import ProductForm
from PIL import Image
import uuid

LOGIN_REDIRECT_URL = '/admin/login/'


@method_decorator(login_required(login_url=LOGIN_REDIRECT_URL), name='dispatch')
class AdminAuth(View):
    pass


class WithHeader(ContextMixin):
    page_header = None
    def get_page_header(self):
        return self.page_header

    def get_context_data(self, **kwargs):
        ctx = super(WithHeader, self).get_context_data(**kwargs)
        if self.get_page_header():
            ctx['page_header'] = self.get_page_header()
        else:
            raise ValueError("WithHeader.page_header must be defined!")

        return ctx


class AdminContext(ContextMixin, AdminAuth):

    def get_context_data(self, **kwargs):
        ctx = super(AdminContext, self).get_context_data()
        ctx.update({'site_name': settings.SITE_NAME})

        return ctx



def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active and user.is_superuser:
                login(request, user)
                return redirect(to='/admin')
            else:
                err_text = 'Пользователь не активен'
        else:
            err_text = 'Неверный логин или пароль'

        return render(request, 'login.html', context={
            "error": err_text,
        })

    else:
        ctx = {'already_logged': False}
        if request.user.is_authenticated():
            ctx['already_logged'] = True

        return render(request, 'login.html', context=ctx)


def admin_logout(request):
    logout(request)
    return redirect(to=reverse('login'))


class AdminIndex(TemplateView, AdminContext, WithHeader):
    page_header = "Панель управления"
    template_name = 'admin_index.html'


class ProductsList(ListView, AdminContext, WithHeader):
    page_header = 'Продукты'
    template_name = 'products/list.html'
    queryset = models.Product.objects.all()
    context_object_name = 'products'
    ordering = 'id'

    def get_context_data(self, **kwargs):
        ctx = super(ProductsList, self).get_context_data()
        ctx['products'] = self.get_queryset()

        return ctx


class ProductCreate(CreateView, AdminContext, WithHeader):
    page_header = 'Добавить продукт'
    template_name = 'products/create.html'

    model = models.Product
    fields = ['name', 'cost', 'count', ]
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreate, self).get_context_data()
        ctx['form'] = self.get_form()

        return ctx

    def get_form(self, form_class=None):
        form = super(ProductCreate, self).get_form()

        return form

    def get_parent_link(self):
        return reverse('products_list')

    def form_valid(self, form):
        product = form.save(commit=False)
        product.save()
        return super(ProductCreate, self).form_valid(form)

    def get_success_url(self):
        return '../%s/' % self.object.id


class ProductUpdate(UpdateView, AdminContext, WithHeader):
    page_header = 'Изменить продукт'
    template_name = 'products/update.html'

    model = models.Product
    fields = ['name', 'cost', 'count', ]
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data()
        ctx['form'] = self.get_form()

        images_qs = self.object.thumbs
        ctx['images'] = images_qs

        return ctx

    def get_form(self, form_class=ProductForm):
        form = super(ProductUpdate, self).get_form()
        # images = self.object.get_images()
        # img_urls = []
        # for i in images:
        #     img_urls.append(i.thumbnail.url)
        # form.fields['images'] = forms.ImageField()
        # form.fields['images'].initial = images

        return form


    def get_parent_link(self):
        return reverse('products_list')

    def get_object(self, queryset=None):
        return get_object_or_404(
                self.model,
                id=self.kwargs['pk']
        )

    def get_success_url(self):
        return '../%s/' % self.object.id

# TODO: implement this class properly!!
class ProductView(DetailView, AdminContext, WithHeader):
    page_header = 'Изменить продукт'
    template_name = 'products/update.html'

    model = models.Product
    fields = ['name', 'cost', 'count', ]
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super(ProductView, self).get_context_data()
        # ctx['form'] = self.get_form()
        # ctx['form'].fields['images'] = self.object.get_images()
        # images = self.object.get_images()
        # img_urls = []
        # for i in images:
        #     img_urls.append(i.thumbnail.url)
        # form.fields['images'] = forms.ImageField()
        # form.fields['images'].initial = images
        ctx['images'] = self.object.get_images()

        return ctx

    def get_parent_link(self):
        return reverse('products_list')

    def get_object(self, queryset=None):
        return get_object_or_404(
                self.model,
                id=self.kwargs['pk']
        )

    def get_success_url(self):
        return '../%s/' % self.object.id


class ProductRemove():
    pass


class ImageCreate(CreateView, AdminContext, WithHeader):
    page_header = 'Добавить изображение'
    template_name = 'images/create.html'

    model = models.ProductImage
    fields = ['product', 'image' ]
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        ctx = super(ImageCreate, self).get_context_data()
        ctx['form'] = self.get_form()

        return ctx

    def post(self, request, *args, **kwargs):
        image = self.request.FILES.get('image')
        name = image.name
        splitted = name.split('.')
        ext_idx = len(splitted) - 1
        ext = splitted[ext_idx]
        image.name = str(uuid.uuid4()) + '.' + str(ext)

        product_id = self.request.POST.get('product')

        return super(ImageCreate, self).post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(ImageCreate, self).get_form()

        return form

    def form_invalid(self, form):

        return super(ImageCreate, self).form_invalid(form)

    def form_valid(self, form):
        image = form.save(commit=False)
        product_id = self.request.POST.get('product')
        product = models.Product.objects.get(id=product_id)
        image.product = product
        image.save()

        size = (600, 600)

        full_link = image.image.file.name
        infile = Image.open(full_link)
        outfile = infile.fp.name.split('.')[0] + '_thumb' + '.jpg'

        if infile != outfile:
            try:
                infile.thumbnail(size)
                infile.save(outfile, "JPEG")
            except IOError:
                print("cannot create thumbnail for", infile)

        rel_name_spl = outfile.split('/')
        file_idx = len(rel_name_spl) - 1
        dir_idx = len(rel_name_spl) - 2
        image.thumb = rel_name_spl[dir_idx] + '/' + rel_name_spl[file_idx]
        image.save()


        return super(ImageCreate, self).form_valid(form)

    def get_success_url(self):
        return '../%s/' % self.object.id


class ImageRemove(CreateView, AdminContext, WithHeader):
    page_header = 'Добавить изображение'
    template_name = 'images/create.html'

    model = models.ProductImage
    fields = ['product', 'image' ]
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        ctx = super(ImageRemove, self).get_context_data()
        ctx['form'] = self.get_form()

        return ctx

    def post(self, request, *args, **kwargs):
        # image = self.request.FILES.get('image')
        # name = image.name
        # splitted = name.split('.')
        # ext_idx = len(splitted) - 1
        # ext = splitted[ext_idx]
        # image.name = str(uuid.uuid4()) + '.' + str(ext)
        #
        # product_id = self.request.POST.get('product')

        return super(ImageRemove, self).post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(ImageRemove, self).get_form()

        return form

    def form_invalid(self, form):

        return super(ImageRemove, self).form_invalid(form)

    def form_valid(self, form):
        image = form.save(commit=False)
        full_link = image.image.file.name

        return super(ImageRemove, self).form_valid(form)

    def get_success_url(self):
        return '../%s/' % self.object.id