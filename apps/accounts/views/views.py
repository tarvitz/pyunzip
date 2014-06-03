# Create your views here.
# -*- coding: utf-8 -*-
from django.views import generic
from django.contrib import auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from apps.core.helpers import render_to
from apps.core.views import (
    LoginRequiredMixin
)
from apps.accounts.forms import (
    LoginForm, ProfileForm, RegisterForm
)
from apps.accounts.models import (
    User
)



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
        kwargs.update({
            'instance': self.request.user, 'request': self.request})
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
        if not user.is_active:
            return redirect(reverse_lazy('accounts:banned'))
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
        return reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = User.objects.create(username=form.cleaned_data['username'],
                                   email=form.cleaned_data['email'],
                                   nickname=form.cleaned_data['nickname'])
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect(self.get_success_url())


class ProfileSelfView(generic.TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileSelfView, self).get_context_data(**kwargs)
        context.update({'object': self.request.user})
        return context


class ProfileView(generic.DetailView):
    template_name = 'accounts/profile.html'
    model = User
    slug_field = 'nickname'

    def get_queryset(self):
        if 'nickname' in self.kwargs:
            return super(ProfileView, self).get_queryset().filter(
                nickname__iexact=self.kwargs.get('nickname', '!void')
            )
        return super(ProfileView, self).get_queryset()