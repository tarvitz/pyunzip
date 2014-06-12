# coding: utf-8

from django.core.exceptions import PermissionDenied

from django.shortcuts import redirect
from apps.helpers.diggpaginator import DiggPaginator as Paginator

from django.shortcuts import get_object_or_404
from apps.karma.models import Karma
from apps.karma.forms import KarmaForm

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.karma.decorators import (
    day_expired,

)

from django.views import generic
from django.utils.decorators import method_decorator
from django.conf import settings


class KarmaChangeView(generic.FormView):
    form_class = KarmaForm
    template_name = 'karma/karma_change.html'

    @method_decorator(day_expired)
    def dispatch(self, request, *args, **kwargs):
        return super(KarmaChangeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(KarmaChangeView, self).get_form_kwargs()
        kwargs.update({
            'initial': {
                'url': self.request.META.get('HTTP_REFERER', '/')
            }
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(KarmaChangeView, self).get_context_data(**kwargs)
        requestee = get_object_or_404(
            User, nickname__icontains=self.kwargs.get('nickname', '!void')
        )
        context.update({
            'requestee': requestee,
            'choice': self.kwargs.get('choice', 'down')
        })
        return context

    def form_valid(self, form):
        comment = form.cleaned_data['comment']
        voter = self.request.user
        url = form.cleaned_data['url']
        user = get_object_or_404(
            User, nickname__iexact=self.kwargs.get('nickname', '!void'))
        if voter == user:
            raise PermissionDenied()
        value = 1 if self.kwargs.get('choice', 'down') == 'up' else -1
        Karma.objects.create(user=user, voter=voter, comment=comment,
                             value=value, url=url)
        return redirect(user.get_absolute_url())


class KarmaListView(generic.ListView):
    model = Karma
    paginate_by = settings.OBJECTS_ON_PAGE
    paginator_class = Paginator
    template_name = 'karma/karma_list.html'

    def get_context_data(self, **kwargs):
        context = super(KarmaListView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        user = self.request.user
        if pk:
            user = get_object_or_404(User, pk=pk)
        context.update({
            'usr': user
        })
        return context

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        qs = super(KarmaListView, self).get_queryset()
        if pk:
            return qs.filter(user__pk=pk)
        return qs.filter(user=self.request.user)