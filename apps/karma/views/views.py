# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.shortcuts import redirect
from apps.core.shortcuts import direct_to_template
from django.shortcuts import get_object_or_404
from apps.core import get_skin_template
from apps.karma.models import Karma, KarmaStatus
from apps.karma.forms import AlterKarmaForm, KarmaModelForm
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

from datetime import datetime
from apps.karma.decorators import (
    day_expired, amount_comments_required,

)

from apps.core.helpers import paginate
from apps.core.helpers import can_act, render_to
from django.views import generic
from django.utils.decorators import method_decorator
from django.conf import settings


#old and deprecated
#@twenty_comments_required
@login_required
@amount_comments_required(settings.KARMA_COMMENTS_COUNT)
@day_expired
@can_act
def alter_karma(request, choice=None, nickname=None):
    #choice may be up|down
    template = get_skin_template(request, 'alter_karma.html')
    alter_status_template = get_skin_template(request, 'alter_status.html')
    if request.method == 'POST':
        form = AlterKarmaForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            now = datetime.now()
            voter = request.user
            user_nickname = form.cleaned_data['hidden_nickname']
            referer = form.cleaned_data['referer']
            url = form.cleaned_data['url']
            try:
                user = User.objects.get(nickname__iexact=user_nickname)
            except User.DoesNotExist:
                return HttpResponseRedirect('/user/does/not/exist')
            if voter == user:
                return HttpResponseRedirect('/users/are/ident/')
            #set default value to alter
            if choice in 'up': value = 1
            else: value = -1
            k = Karma(user=user, voter=voter,
                comment=comment, date=now, value=value, url=url)
            k.save()
            """
            fraction_ident = check_fraction(user, voter)
            if fraction_ident:
                k = Karma(user=user, voter=voter, comment=comment, date=now, value=value, url=url)
                k.save()
            #dangers of warp ;) 75% to fail karma's alter
            else:
                if randint(1, 100)>=75: #75
                    #20% chance to alter karma with overside value
                    if randint(1, 100)>=80:
                        comment = comment + " [warp's instability]"
                        k = Karma(user=user, voter=voter, comment=comment, date=now, value=value*-1, url=url)
                    else:
                        k = Karma(user=user, voter=voter, comment=comment, date=now, value=value, url=url)
                    k.save()
                    return HttpResponseRedirect(referer)
                    #bad idea ? :)
                    #direct_to_template(request, alter_status_template,{'alter_status':True})
                else:
                    #failed! ;)
                    k = Karma(user=user, voter=voter, comment=comment, date=now, value=0, url=url)
                    k.save()
                    return direct_to_template(request,
                            alter_status_template,{'alter_status':False})
            """
            return HttpResponseRedirect(referer)
        else:
            return direct_to_template(request, template, {'form':form})
    else:
        form = AlterKarmaForm()
        form.fields['hidden_nickname'].initial = nickname
        referer = request.META.get('HTTP_REFERER', '/')
        form.fields['referer'].initial = referer
        #MAY BE there is more simple and clear way to capture URL where we got karma ups/downs
        url = referer.replace('://', '')
        form.fields['url'].initial = url[url.index('/'):]
        return direct_to_template(request, template, {'form':form})

@login_required
@amount_comments_required(settings.KARMA_COMMENTS_COUNT)
@day_expired
@can_act
@render_to('alter_karma.html')
def karma_alter(request, choice, nickname):
    user = get_object_or_404(User, nickname__iexact=nickname)
    url = request.META.get('HTTP_REFERER', '/')
    form = KarmaModelForm(
        request.POST or None, request=request,
        initial={
            'user': user.id,  # backward compatiblity
            'alter': choice,
            'url': url
        }
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': form.instance.url or '/'}
    return {
        'form': form
    }

def show_karma(request, user=None, type='', group=False):
    template = get_skin_template(request.user, 'karma.html')
    if not user:
        karmas = Karma.objects.filter(user=request.user)
    else:
        karmas = Karma.objects.filter(user__nickname__iexact=user)
    if 'positive' in type:
        karmas = karmas.filter(value__gt=0)
    elif 'negative' in type:
        karmas = karmas.filter(value__lt=0)
    elif 'zero' in type:
        karmas = karmas.filter(value=0)
    #settings
    show_null = False
    show_self_null = False
    if user is not None:
        if not show_null:
            karmas = karmas.exclude(value=0)
    else:
        if not show_self_null:
            karmas = karmas.exclude(value=0)
    if group:
        pass
    _pages_ = settings.OBJECTS_ON_PAGE
    #paginator = Paginator(karmas, _pages_)
    #try:
    page = request.GET.get('page', 1)
    #    karmas = paginator.page(page)
    #    karmas.number = int(page)
    #except (InvalidPage, EmptyPage):
    #    karmas = paginator.page(1)
    #    karmas.number = 1
    karmas = paginate(karmas, page, pages=_pages_)
    return direct_to_template(request, template,{'karmas':karmas, 'page':karmas})

def show_karmastatus_description(request, id=None, codename=None):
    if id is None and codename is None:
        return HttpResponseRedirect('/')
    template = get_skin_template(request.user, 'karma/description.html')
    try:
        if codename:
            status = KarmaStatus.objects.get(codename__iexact=codename)
        elif id:
            status = KarmaStatus.objects.get(id=id)
        img = "%s/images/karma/status/%s.jpg" % (settings.MEDIA_ROOT, status.codename)
        from os import stat
        try:
            stat(img)
            img = "images/karma/status/%s.jpg" % (status.codename)
        except OSError:
            img = "images/karma/status/_none_"
    except:
            return HttpResponseRedirect('/')
    return direct_to_template(request, template,
        {'status':status,
        'img': img})


class KarmaChangeView(generic.FormView):
    form_class = AlterKarmaForm
    template_name = 'karma/karma_change.html'

    @method_decorator(day_expired)
    def dispatch(self, request, *args, **kwargs):
        return super(KarmaChangeView, self).dispatch(request, *args, **kwargs)

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