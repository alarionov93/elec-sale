from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin, View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView

LOGIN_REDIRECT_URL = '/admin/login/'


@method_decorator(login_required(login_url=LOGIN_REDIRECT_URL), name='dispatch')
class AdminMixin(View):
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


def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active and user.is_admin:
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


class AdminIndex(TemplateView, AdminMixin, WithHeader):
    page_header = "Панель управления"
    template_name = 'admin_index.html'



class ProductsList(ListView, AdminMixin, WithHeader):
    page_header = 'Продукты'


class ProductCreate(CreateView, AdminMixin, WithHeader):
    page_header = 'Добавить продукт'


class ProductUpdate(UpdateView, AdminMixin, WithHeader):
    page_header = 'Изменить продукт'