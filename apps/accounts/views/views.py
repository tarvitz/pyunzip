# Create your views here.
# -*- coding: utf-8 -*-
from apps.core.helpers import render_to, get_object_or_404
from utils.paginator import DiggPaginator as Paginator
from apps.core.views import (
    RequestMixin, LoginRequiredMixin
)
from apps.accounts.forms import (
    LoginForm, ProfileForm, RegisterForm
)

from apps.accounts.models import (
    User
)
from django.views import generic
from django.contrib import auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy


#mixins
class AdminMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('accounts:login')
        dispatch = super(AdminMixin, self).dispatch(
            request, *args, **kwargs
        )
        return dispatch


class OperatorMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_operator:
            return redirect('accounts:login')
        dispatch = super(OperatorMixin, self).dispatch(
            request, *args, **kwargs
        )
        return dispatch


class AdminOrOpertorMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not any([request.user.is_admin, request.user.is_operator]):
            return redirect('accounts:login')
        dispatch = super(AdminOrOpertorMixin, self).dispatch(
            request, *args, **kwargs
        )
        return dispatch


class NonUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not any([request.user.is_admin, request.user.is_teacher,
                    request.user.is_operator]):
            return redirect('accounts:login')
        return super(NonUserMixin, self).dispatch(
            request, *args, **kwargs
        )


# plain views
@render_to('accounts/login.html')
def login(request, form_class=LoginForm):
    form = form_class(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            auth.login(request, user)
            nxt = request.POST.get('next', request.GET.get('next', None))
            return {'redirect': nxt or 'core:index'}
    return {
        'form': form
    }


@render_to('index.html')
def logout(request):
    auth.logout(request)
    return {}


@login_required
@render_to('index.html')
def user_set_context(request, context):
    request.user.set_context(context)
    return {'redirect': request.META.get('HTTP_REFERER', '/')}


@login_required
def user_switch_context(request):
    context = request.GET.get('role', '')
    return user_set_context(
        request, context=request.user.get_context_id(context)
    )


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    model = User
    template_name = 'accounts/profile.html'

    def get_queryset(self):
        return super(ProfileView, self).get_queryset().filter(
            pk=self.request.user.pk
        )


class ProfileUpdateView(LoginRequiredMixin, generic.FormView):
    model = User
    form_class = ProfileForm
    success_url = reverse_lazy('accounts:profile')

    template_name = 'accounts/profile_update.html'

    def get_form_kwargs(self):
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs.update({'instance': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('pybb:index')

    def form_valid(self, form):
        user = form.cleaned_data['user']
        auth.login(self.request, user)
        return redirect(self.get_success_url())


class LogoutView(generic.View):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        auth.logout(self.request)
        return redirect(reverse_lazy('accounts:login'))


class RegisterView(generic.FormView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'

    def get_success_url(self):
        return reverse_lazy('wh:profile')

    def form_valid(self, form):
        user = User.objects.create(username=form.cleaned_data['username'],
                                   email=form.cleaned_data['email'],
                                   nickname=form.cleaned_data['nickname'])
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect(self.get_success_url())