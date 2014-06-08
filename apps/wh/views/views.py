# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.wh.models import Rank
from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from apps.core.decorators import has_permission

from django.core import serializers

from apps.wh.forms import SuperUserLoginForm

from apps.core import get_skin_template
from datetime import datetime, timedelta


from django.http import Http404
from apps.news.templatetags.newsfilters import spadvfilter
from django.template.defaultfilters import striptags

from apps.core.shortcuts import direct_to_template
from django.shortcuts import redirect
from apps.core.helpers import (
    paginate, can_act, get_object_or_None,
    safe_ret, get_int_or_zero
)
from django.conf import settings


def superuser_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_superuser:
            return func(*args, **kwargs)
        else:
            return redirect('/permission/denied')
    return wrapper


@superuser_required
def sulogin(request):
    referer = request.META.get('HTTP_REFERER', '/')
    form = SuperUserLoginForm(request.POST or None)
    if request.method == 'POST':
        username = request.POST['username']
        user = get_object_or_None(User, username=username)
        if user:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            return redirect(request.GET.get('next') or '/')
        else:
            raise Http404("no such user")
    return render_to_response(
        'accounts/login.html', {
            'next': referer,
            'referer': referer,
            'form': form
        },
        context_instance=RequestContext(request)
    )


# todo: move to accounts
@login_required
def users(request):
    template = get_skin_template(request.user, 'accounts/index.html')
    page = get_int_or_zero(request.GET.get('page')) or 1
    users = User.objects.filter(is_active=True).order_by('date_joined')
    _pages_ = settings.OBJECTS_ON_PAGE
    users = paginate(users, page, pages=_pages_)
    return render_to_response(
        template,
        {
            'users': users,
            'page': users
        },
        context_instance=RequestContext(request)
    )


def show_rank(request, pk=None, codename=None):
    from os import stat
    if pk is None and codename is None:
        return redirect('/')
    template = get_skin_template(request.user, 'ranks/rank.html')
    rank = None
    try:
        if codename:
            rank = Rank.objects.get(codename__exact=codename)
        elif pk:
            rank = Rank.objects.get(pk=pk)
        img = "%s/images/ranks/%s/%s.jpg" % (
            settings.MEDIA_ROOT, rank.type.type.lower(), rank.codename
        )
        try:
            stat(img)
            img = "images/ranks/%s/%s.jpg" % (rank.type.type.lower(), rank.codename)
        except OSError:
            img = "images/ranks/_none_.jpg"
    except Rank.DoesNotExist:
        return redirect('/')
    return render_to_response(
        template,
        {
            'rank': rank,
            'img': img
        },
        context_instance=RequestContext(request)
    )


def get_rank(request, codename=None, pk=None, raw=True):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    qset = Q()
    if codename:
        qset = Q(codename__exact=codename)
    elif pk:
        qset = Q(pk=pk)
    else:
        pass
    try:
        rank = Rank.objects.get(qset)
        # FIXME: :(
        from time import sleep
        sleep(0.125)
        if not raw:
            rank.description = striptags(rank.description)
            rank.description = spadvfilter(rank.description)
        response.write(serializers.serialize("json", [rank]))
        return response
    except Rank.DoesNotExist:
        msg_error = u"no rank"
        return HttpResponseServerError(msg_error)


@has_permission('wh.set_warnings')
@can_act
def alter_warning(request, nickname, typ):
    """alter_warning could increase or decrease warning level of the user """
    from apps.wh.models import Warning, WarningType
    user = get_object_or_404(User, nickname__iexact=nickname)
    warnings = Warning.objects.filter(user__nickname__iexact=nickname)

    #if typ in 'increase':
    #    type_offset = 1
    #if typ in 'decrease':
    #    type_offset = -1

    type_offset = 1 if typ == 'increase' else -1
    if warnings:
        #fixing instabillity
        if len(warnings) > 1:
            for n in xrange(1, len(warnings) - 1):
                #Instabillity
                warnings[n].remove()
        old_warning = warnings[0]

        # FIXME: we should use more strict expired schema
        from datetime import datetime, timedelta
        expired = datetime.now() + timedelta(
            days=int(old_warning.level) * 7
        )
        new_warning = Warning(
            user=user,
            level=int(old_warning.level) + type_offset,
            expired=expired,
            style='color:red;'
        )
        #search for a type
        # NOTICE that block could be dangerous because there could not
        # be nor general warningtype nor common!
        if typ in 'decrease' and int(old_warning.level) == 1:
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.comments.models import Comment
            ct = ContentType.objects.get(app_label='wh', model='warning')
            try:
                comments = Comment.objects.filter(
                    content_type=ct, object_pk=str(old_warning.pk)
                )
                if comments:
                    for c in comments:
                        c.delete()
            except Comment.DoesNotExist:
                #do nothing
                pass
            old_warning.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        try:
            warning_type = WarningType.objects.get(
                side=safe_ret(user, 'army.side'),
                level=int(old_warning.level) + type_offset
            )
        except WarningType.DoesNotExist:
            try:
                warning_type = WarningType.objects.get(
                    level=int(old_warning.level) + type_offset,
                    is_general=True
                )
            except WarningType.DoesNotExist:
                return redirect(request.META.get('HTTP_REFERER', '/'))

        new_warning.type = warning_type
        new_warning.save()
    else:
        #we can not decreese null warnings :)
        if typ in 'decrease':
            return redirect(request.META.get('HTTP_REFERER', '/'))
        #there is no warnings
        try:
            #common_warning contains warning message for each side
            warning_type = WarningType.objects.get(
                side=safe_ret(user, 'army.side'),
                level=1
            )
        except WarningType.DoesNotExist:
            #we fail, so we search for general warning, JUST FOR ALL
            warning_type = WarningType.objects.get(level=1, is_general=True)
        from datetime import datetime, timedelta
        expired = datetime.now() + timedelta(days=7)
        warning = Warning(
            type=warning_type, user=user, level=1,
            style='color:red;', expired=expired
        )
        warning.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@has_permission('wh.set_warnings')
@can_act
def alter_warning_form(request, nickname):
    #implement here an free warning alteration
    from apps.wh.models import Warning, WarningType
    template = get_skin_template(request.user, 'warnings/alter.html')
    from apps.wh.forms import WarningForm
    warn_user = get_object_or_404(User, nickname__iexact=nickname)
    if request.method == 'POST':
        form = WarningForm(request.POST or None, request=request)
        if form.is_valid():
            level = int(form.cleaned_data['level'])
            comment = form.cleaned_data['comment']
            #nickname = form.cleaned_data['nickname']
            referer = form.cleaned_data['next']
            try:
                warning_type = WarningType.objects.get(
                    side=safe_ret(warn_user, 'army.side'),
                    level=level
                )
            except WarningType.DoesNotExist:
                #it's a little bit dangerous
                warning_type = WarningType.objects.get(
                    is_general=True, level=level
                )
            expired = datetime.now() + timedelta(days=level * 7)
            warning = Warning(
                type=warning_type,
                user=warn_user, level=level,
                expired=expired, style='color: red;'
            )
            warning.save()
            if comment:
                #saving comment for warning alteration
                from django.contrib.contenttypes.models import ContentType
                from django.contrib.comments.models import Comment
                ct = ContentType.objects.get(app_label='wh', model='warning')
                c = Comment(
                    content_type=ct, object_pk=str(warning.pk),
                    user=request.user,
                    comment=comment, submit_date=datetime.now(),
                    is_public=True, site_id=1
                )
                c.save()
            return redirect(referer or '/')
        else:
            return direct_to_template(request, template, {'form': form})
    else:
        try:
            warning = Warning.objects.get(user=warn_user)
            level = int(warning.level)
        except Warning.DoesNotExist:
            level = 1
        form = WarningForm(request=request)
        form.fields['level'].initial = level
        form.fields['nickname'].initial = warn_user.nickname
        form.fields['next'].initial = request.META.get('HTTP_REFERER', '/')
    return direct_to_template(request, template, {'form': form})