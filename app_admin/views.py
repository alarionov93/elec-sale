from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin, View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from core import models
from app_admin.forms import ProductForm

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
    fields = ['name', 'cost', ]
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super(ProductCreate, self).get_context_data()
        ctx['form'] = self.get_form()

        return ctx

    def get_form(self, form_class=ProductForm):
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
    fields = ['name', 'cost', ]
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data()
        ctx['form'] = self.get_form()

        return ctx

    def get_form(self, form_class=ProductForm):
        form = super(ProductUpdate, self).get_form()

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


class ProductRemove():
    pass