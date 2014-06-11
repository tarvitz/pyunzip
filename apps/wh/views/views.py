# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.wh.models import Rank

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import auth

from apps.wh.forms import SuperUserLoginForm
from apps.core import get_skin_template

from django.http import Http404
from django.shortcuts import redirect
from apps.core.helpers import (
    get_object_or_None,
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
