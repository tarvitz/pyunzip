# Create your views here.
# -*- coding: utf-8 -*-
from apps.core.helpers import render_to, get_object_or_404
from apps.core.diggpaginator import DiggPaginator as Paginator
from apps.core.views import (
    RequestMixin, LoginRequiredMixin, DjangoFilterMixin
)
from apps.accounts.forms import (
    LoginForm, AccountRequestForm,
    AccountRequestUpdateForm, AgreeForm, AddRoleForm,
    UpdateRoleForm, ProfileForm,
)
from apps.accounts.filters import RoleFilter
from apps.accounts.models import (
    AccountRequest, User
)
from django.views.generic import (
    CreateView, UpdateView, ListView, FormView, TemplateView
)
from django.http import Http404
from django.contrib import auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import mail
from django.template.loader import render_to_string
from django.template.defaultfilters import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


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


@render_to('accounts/register.html')
def register(request):
    #view = RegisterWizard.as_view([AccountRequestForm, AccountRequesteeFormset])
    #response = view(request)
    #return response
    form = AccountRequestForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': 'accounts:register-success'}
    return {'form': form}


class RequestListView(ListView):
    model = AccountRequest
    paginate_by = settings.OBJECTS_ON_PAGE
    paginator_class = Paginator

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not any((user.is_admin, user.is_auditor, user.is_secretary)):
            return redirect('core:permission-denied')
        return super(RequestListView, self).dispatch(
            request, *args, **kwargs
        )

    def get_template_names(self):
        return "{path}/{template_name}".format(
            path=self.model._meta.app_label,
            template_name='request_list.html'
        )

    def get_queryset(self):
        return super(RequestListView, self).get_queryset().filter(
            is_user_created=False
        )


class UpdateRequestView(RequestMixin, UpdateView):
    model = AccountRequest
    form_class = AccountRequestUpdateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not any((user.is_admin, user.is_auditor, user.is_secretary)):
            return redirect('core:permission-denied')
        return super(UpdateRequestView, self).dispatch(
            request, *args, **kwargs
        )

    def get_template_names(self):
        path = self.model._meta.app_label
        return '{path}/{template_name}'.format(
            path=path,
            template_name='request_update.html'
        )

    def get_success_url(self):
        return reverse('accounts:requests')


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


class CreateAccountView(FormView):
    form_class = AgreeForm

    def get_template_names(self):
        return 'accounts/create_account_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateAccountView, self).get_context_data(
            **kwargs
        )
        instance = get_object_or_404(AccountRequest, pk=self.kwargs['pk'])
        context.update({'instance': instance})
        return context

    def form_valid(self, form):
        instance = get_object_or_404(AccountRequest, pk=self.kwargs['pk'])
        instance.create_account()
        return redirect('accounts:requests')


class RoleListView(LoginRequiredMixin, AdminMixin,
                   DjangoFilterMixin,
                   ListView):
    model = User
    paginator_class = Paginator
    paginate_by = settings.OBJECTS_ON_PAGE
    filter_class = RoleFilter

    def get_template_names(self):
        return 'accounts/role_list.html'

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(RoleListView, self).dispatch(
            request, *args, **kwargs
        )
        #if not any([request.user.is_admin, request.user.is_operator]):
        #    raise Http404("Not allowed")
        return dispatch

    def get_queryset(self):
        return super(RoleListView, self).get_queryset().filter(
            #is_teacher=True
        )


class CreateRoleView(LoginRequiredMixin, AdminMixin,
                     CreateView):
    model = User
    form_class = AddRoleForm

    success_url = reverse_lazy('accounts:roles')

    def get_template_names(self):
        return 'accounts/role_create.html'

    def form_valid(self, form):
        html = render_to_string('mail/role_account.html', {
            'instance': form.instance,
            'login_url': '%s%s' % (settings.RESOURCE_HOST,
                                   settings.LOGIN_URL),
            # could be a little bit insecure, be warned
            'password': form.cleaned_data['password'],
        })
        message = mail.EmailMultiAlternatives(
            unicode(_("Account information")), strip_tags(html),
            settings.FROM_EMAIL, [form.instance.email]
        )
        message.attach_alternative(html, 'text/html')
        message.send(fail_silently=True)
        return super(CreateRoleView, self).form_valid(form)


class UpdateRoleView(LoginRequiredMixin, AdminMixin,
                     UpdateView):
    model = User
    form_class = UpdateRoleForm
    success_url = reverse_lazy('accounts:roles')

    def get_object(self, queryset=None):
        object = super(UpdateRoleView, self).get_object(queryset)
        #if not object.is_teacher:
        #    raise Http404("Not a teacher")
        return object

    def get_template_names(self):
        return 'accounts/role_update.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'accounts/profile.html'

    def get_queryset(self):
        return super(ProfileView, self).get_queryset().filter(
            pk=self.request.user.pk
        )


class ProfileUpdateView(LoginRequiredMixin, FormView):
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