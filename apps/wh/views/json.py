# coding: utf-8
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from apps.wh.models import MiniQuote, Army, Expression, PM
from django.shortcuts import get_object_or_404
from apps.core.helpers import render_to, render_to_json, get_int_or_zero
from apps.core.decorators import login_required_json
from django.utils.html import strip_tags

def miniquote(request):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    try:
        mq = MiniQuote.objects.order_by('?')[0]
    except IndexError:
        response.write('false')
        return response
    response.write(serializers.serialize("json",[mq]))

    return response

def army(request, id=None):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    if not id:
        response.write("[]")
        return response
    armies = Army.objects.filter(side__id=id)
    response.write(serializers.serialize("json", armies))
    return response

@render_to_json(content_type='application/json')
def expression(request):
    return {
        'expression': Expression.objects.order_by('?').all()[0]
    }

@login_required
@render_to_json(content_type='application/json')
def pm(request):
    folder = request.GET.get('folder', 'inbox')
    if folder == 'inbox':
        pm = PM.objects.filter(addressee=request.user, dba=False)
    elif folder == 'outbox':
        pm = PM.objects.filter(sender=request.user, dbs=False)
    elif folder == 'deleted':
        pm = PM.objects.filter(dbs=True)
    else:
        return {}
    _pm = []
    pm = pm.order_by('-is_read', '-sent')
    for p in pm:
        _pm.append({
            'to': p.addressee.nickname or p.addressee.username,
            'from': p.sender.nickname or p.addressee.username,
            'date': p.sent.strftime('%Y-%m-%d %H:%M'),
            'subject': p.title,
            'folder': folder,
            'is_read': p.is_read,
            'id': p.pk
        })
    return {'id': folder, 'mails': _pm}


@login_required
@render_to_json(content_type='application/json')
def pm_view(request):
    pk = get_int_or_zero(request.GET.get('pk')) or 0
    folder = request.GET.get('folder', 'inbox')
    if folder not in ('inbox', 'outbox', 'deleted'):
        raise Http404("hands off")
    message = get_object_or_404(PM, pk=pk)
    if request.user not in (message.addressee, message.sender):
        raise Http404("stay away")

    avatar, nickname, nick_id = (None, None, None)
    if folder == 'inbox':
        avatar = message.sender.get_avatar_url()
        nickname = message.sender.get_nickname()
        nick_id = message.sender.pk
    elif folder in ('outbox', 'deleted'):
        avatar = message.addressee.get_avatar_url()
        nickname = message.addressee.get_nickname()
        nick_id = message.addressee.pk
    else:
        pass
    
    msg = {
        'id': message.pk,
        'to': message.addressee.nickname or message.addressee.username,
        'from': message.sender.nickname or message.sender.username,
        'date': message.sent.strftime('%Y-%m-%d %H:%M'),
        'subject': message.title,
        'content': message.cache_content,
        'folder': folder,
        'avatar': avatar,
        'nickname': nickname,
        'nick_raw': strip_tags(nickname),
        'nick_id': nick_id,
        'is_read': message.is_read
    }
    if not message.is_read and folder == 'inbox':
        message.is_read = True
        message.save()
    return msg


@login_required_json
@render_to_json(content_type='application/json')
def pm_unread(request):
    count = PM.objects.filter(addressee=request.user, is_read=False).count()
    return {'pm_unread': count}


@render_to_json(content_type='application/json')
def users(request):
    q = request.GET.get('q', '')
    users = User.objects.filter(nickname__icontains=q)[:30]
    _users = []
    for user in users:
        _users.append({
            'id': user.pk,
            'title': user.nickname
        })
    return _users
