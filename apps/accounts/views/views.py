# Create your views here.
# -*- coding: utf-8 -*-
from django.views import generic

from django.db.models import Q
from django.contrib import auth
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.utils.text import force_text
from django.conf import settings

from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.core.models import UserSID
from apps.core.helpers import get_object_or_None, get_object_or_404
from apps.core.views import (
    LoginRequiredMixin
)
from apps.accounts.forms import (
    LoginForm, ProfileForm, RegisterForm,
    PasswordChangeForm,
    PasswordRestoreForm, PasswordRestoreInitiateForm, PMForm, PMReplyForm,
    PolicyWarningForm
)
from apps.core.views import RequestMixin
from apps.accounts.models import (
    User, PM, PolicyWarning
)


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


class PasswordRestoreInitiateView(generic.FormView):
    form_class = PasswordRestoreInitiateForm
    success_url = reverse_lazy('core:password-restore-initiated')
    template_name = 'accounts/password_restore_initiate.html'

    def form_valid(self, form):
        users = form.cleaned_data['users']
        sids = UserSID.objects.filter(user__in=users, expired=True)
        sids = list(sids)
        if not sids:
            for user in users:
                sid = UserSID.objects.create(user)
                sids.append(sid)
        else:
            for user in users:
                sid = UserSID.objects.filter(
                    user=user).order_by('-id')[0]
                sids.append(sid)
                (lambda x: x)(user)

        for sid in sids:
            msg = settings.PASSWORD_RESTORE_REQUEST_MESSAGE % {
                'link': settings.DOMAIN + "%s" % reverse_lazy(
                    'accounts:password-restore', args=(sid.sid, )
                )
            }
            if settings.SEND_MESSAGES:
                send_mail(
                    subject=force_text(
                        _('Your password requested to change')
                    ),
                    message=force_text(msg),
                    from_email=settings.FROM_EMAIL,
                    recipient_list=[sid.user.email]
                )
        return redirect(self.get_success_url())


class PasswordRestoreView(generic.FormView):
    form_class = PasswordRestoreForm
    success_url = reverse_lazy('core:password-restored')
    template_name = 'accounts/password_restore.html'

    def get_form_kwargs(self):
        kwargs = super(PasswordRestoreView, self).get_form_kwargs()
        sid = self.kwargs.get('sid', 0)
        instance = get_object_or_None(UserSID, sid=sid, expired=False)
        if not instance:
            raise Http404
        kwargs.update({
            'instance': instance,
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class PasswordChangeView(generic.FormView):
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password-changed')

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data['password1']
        user.set_password(password)
        user.save()
        return redirect(self.get_success_url())


class UserListView(generic.ListView):
    model = User
    paginator_class = Paginator
    paginate_by = settings.OBJECTS_ON_PAGE
    template_name = 'accounts/users.html'


class PMMixin(object):
    model = PM
    paginate_class = Paginator
    paginator_by = settings.OBJECTS_ON_PAGE
    template_name = 'accounts/pm_list.html'


class PMInboxListView(PMMixin, generic.ListView):
    def get_context_data(self, **kwargs):
        context = super(PMInboxListView, self).get_context_data(**kwargs)
        context.update({'box': 'inbox'})
        return context

    def get_queryset(self):
        qs = super(PMInboxListView, self).get_queryset()
        return qs.filter(addressee=self.request.user)


class PMOutboxListView(PMMixin, generic.ListView):
    def get_queryset(self):
        qs = super(PMOutboxListView, self).get_queryset()
        return qs.filter(sender=self.request.user)


class PMDetailView(generic.DetailView):
    model = PM
    template_name = 'accounts/pm_detail.html'

    def get_queryset(self):
        qs = super(PMDetailView, self).get_queryset()
        qset = Q(addressee=self.request.user) | Q(sender=self.request.user)
        return qs.filter(qset)

    def get_context_data(self, **kwargs):
        context = super(PMDetailView, self).get_context_data(**kwargs)
        # update its read
        obj = context['object']
        if not obj.is_read and self.request.user == obj.addressee:
            context['object'].is_read = True
            context['object'].save()
        if context['object'].sender == self.request.user:
            context.update({'box': 'outbox'})
        else:
            context.update({'box': 'inbox'})
        initial = {
            'title': (
                obj.title if obj.title.startswith('Re:')
                else 'Re: ' + obj.title
            )}
        context.update({'form': PMReplyForm(initial=initial)})
        return context


class PMReplyView(generic.CreateView):
    model = PM
    template_name = 'accounts/pm_form.html'
    form_class = PMReplyForm
    success_url = reverse_lazy('accounts:pm-outbox')

    def get_pm_object(self):
        if hasattr(self, 'pm_object'):
            return self.pm_object
        self.pm_object = get_object_or_404(PM, pk=self.kwargs.get('pk', 0))

    def get_context_data(self, **kwargs):
        context = super(PMReplyView, self).get_context_data(**kwargs)
        self.get_pm_object()
        context.update({
            'object': self.pm_object
        })
        return context

    def form_valid(self, form):
        self.get_pm_object()
        form.instance.sender = self.request.user
        form.instance.addressee = self.pm_object.sender
        form.instance.syntax = settings.DEFAULT_SYNTAX
        return super(PMReplyView, self).form_valid(form)


class PMSendView(RequestMixin, generic.CreateView):
    model = PM
    template_name = 'accounts/pm_form.html'
    form_class = PMForm
    success_url = reverse_lazy('accounts:pm-outbox')

    def get_context_data(self, **kwargs):
        context = super(PMSendView, self).get_context_data(**kwargs)
        context.update({
            'action': 'send'
        })
        return context


class PolicyWarningAccessMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('accounts.change_policywarning'):
            raise PermissionDenied("not allowed")
        return super(PolicyWarningAccessMixin, self).dispatch(request, *args,
                                                              **kwargs)


class PolicyWarningCreateView(PolicyWarningAccessMixin, generic.CreateView):
    model = PolicyWarning
    form_class = PolicyWarningForm
    template_name = 'accounts/policy_warning_form.html'

    def get_form_kwargs(self):
        kwargs = super(PolicyWarningCreateView, self).get_form_kwargs()
        initial = {
            'user': get_object_or_404(User, pk=self.kwargs.get('pk', 0))
        }
        kwargs.update({
            'initial': initial
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PolicyWarningCreateView, self).get_context_data(
            **kwargs)
        context.update({
            'usr': get_object_or_404(User, pk=self.kwargs.get('pk', 0))
        })
        return context


class PolicyWarningUpdateView(PolicyWarningAccessMixin, generic.UpdateView):
    model = PolicyWarning
    form_class = PolicyWarningForm
    template_name = 'accounts/policy_warning_form.html'


class PolicyWarningDeleteView(PolicyWarningAccessMixin, generic.DeleteView):
    model = PolicyWarning
    template_name = 'accounts/policy_warning_form.html'

    def get_success_url(self):
        return self.object.user.get_policy_warnings_url()

    def get_context_data(self, **kwargs):
        context = super(PolicyWarningDeleteView, self).get_context_data(
            **kwargs)
        context.update({'delete': True})
        return context


class PolicyWarningListView(generic.ListView):
    model = PolicyWarning
    paginator_class = Paginator
    paginate_by = settings.OBJECTS_ON_PAGE
    template_name = 'accounts/policy_warning_list.html'

    def get_queryset(self):
        qs = super(PolicyWarningListView, self).get_queryset()
        if self.request.user.has_perm('accounts.change_policywarning'):
            user_pk = self.kwargs.get('pk', None)
            if user_pk:
                qset = Q(user__pk=user_pk)
                qs = qs.filter(qset)
            return qs
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PolicyWarningListView, self).get_context_data(**kwargs)
        user_pk = self.kwargs.get('pk', None)
        if user_pk:
            context.update({
                'usr': get_object_or_404(User, pk=user_pk)
            })
        return context


class PolicyWarningDetailView(generic.DetailView):
    model = PolicyWarning
    template_name = 'accounts/policy_warning_detail.html'

    def get_queryset(self):
        qs = super(PolicyWarningDetailView, self).get_queryset()
        if self.request.user.has_perm('accounts.change_policywarning'):
            return qs
        return qs.filter(user=self.request.user)
