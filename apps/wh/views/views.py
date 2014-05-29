# Create your views here.
# ^^, coding: utf-8 ^^,
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.wh.models import (
    Side, Army, PM, RegisterSid, Skin, Rank
)
from apps.core.models import UserSID
from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from apps.core.decorators import has_permission, lock_with_dev
from apps.wh.decorators import prevent_bruteforce

from django.core import serializers
from django.core.mail import send_mail
from django.forms.util import ErrorList
from apps.wh.forms import (
    UpdateProfileModelForm, PMForm, RegisterForm,
    PasswordChangeForm, PasswordRecoverForm, LoginForm,
    SuperUserLoginForm,
    PasswordRestoreForm, PasswordRestoreInitiateForm
)

from apps.core import pages, get_skin_template

from PIL import Image
from datetime import datetime, timedelta
from hashlib import sha1
from random import randint, random

from django.http import Http404
from apps.news.templatetags.newsfilters import spadvfilter
from django.template.defaultfilters import striptags

from apps.core.shortcuts import direct_to_template
from django.shortcuts import redirect
from apps.core.helpers import (
    get_settings, get_object_or_none, paginate, can_act,
    handle_uploaded_file, render_to, get_object_or_None,
    safe_ret, get_int_or_zero
)
import os


def superuser_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_superuser:
            return func(*args, **kwargs)
        else:
            return redirect('/permission/denied')
    return wrapper


@render_to('accounts/login.html', allow_xhr=True)
def login(request):
    referer = request.GET.get('next', '/')
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        referer = request.POST.get('next', referer)
        if form.is_valid():
            auth.login(request, form.cleaned_data['user'])
            if referer:
                return {'redirect': referer}
            referer = request.META.get('HTTP_REFERER', '/')
            return {'redirect': referer}
    return {'form': form}


#KIND A HACK o_O
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


def logout(request):
    if hasattr(request.user, 'useractivity'):
        #do not display users whom logged out
        request.user.useractivity.is_logout = True
        request.user.useractivity.save()
    auth.logout(request)
    return redirect('/')


#Поиск по имени рега
#Переписать все это нахуй, стремно как-то выглядит
#upd: 06.10.2010 - внатуре, сижу ржу над топорностью,
#     надо бы переписать и вправду
#upd: 22.04.2013 - надо бы не ругаться :)
@login_required
def profile(request, account_name='self'):
    template = get_skin_template(request.user, 'accounts/profile.html')
    if account_name == 'self':
        return render_to_response(
            template, {
                'usr': request.user,
                '__galleries': '#'
            },  # still not implemented
            context_instance=RequestContext(request))
    try:
        user = User.objects.get(username__exact=account_name)
        permissions = user.user_permissions.all()
    except User.DoesNotExist:
        user = {'errors': _('There is no such user')}
        permissions = {}
    return render_to_response(
        template,
        {
            'usr': user,
            'userperms': permissions
        },
        context_instance=RequestContext(request)
    )


#Поиск по имени ника
@login_required
def profile_by_nick(request, nickname='self'):
    template = get_skin_template(request.user, 'accounts/profile.html')
    from apps.files.models import Gallery
    if nickname == 'self':
        galleries = Gallery.objects.all()
        return render_to_response(
            'accounts/profile.html',
            {
                'usr': request.user,
                'galleries': galleries
            },
            context_instance=RequestContext(request))
    try:
        user = User.objects.get(nickname__exact=nickname)
        galleries = Gallery.objects.filter()
        if not user.is_active:
            return redirect('/user/does/not/exist')
    except User.DoesNotExist:
            return redirect('/user/does/not/exist')

    if hasattr(user, 'user_permissions'):
        permissions = user.user_permissions.all()
    else:
        permissions = dict()

    return render_to_response(
        template,
        {
            'usr': user,
            'userperms': permissions,
            'galleries': galleries
        },
        context_instance=RequestContext(request)
    )


#Все пользователи
@login_required
def users(request):
    template = get_skin_template(request.user, 'accounts/index.html')
    page = get_int_or_zero(request.GET.get('page')) or 1
    users = User.objects.filter(is_active=True).order_by('date_joined')
    _pages_ = get_settings(request.user, 'objects_on_page', 30)
    users = paginate(users, page, pages=_pages_)
    return render_to_response(
        template,
        {
            'users': users,
            'page': users
        },
        context_instance=RequestContext(request)
    )


@login_required
@render_to('accounts/update_profile.html')
def update_profile(request):
    template = get_skin_template(request.user, 'accounts/update_profile.html')
    form = UpdateProfileModelForm(
        request.POST or None, request.FILES or None, instance=request.user,
        request=request
    )
    if request.method == 'POST':
        if form.is_valid():
            if 'avatar' in request.FILES:
                avatar = handle_uploaded_file(
                    request.FILES['avatar'],
                    'avatars/%s' % request.user.id
                )
                form.instance.avatar = avatar
            if 'photo' in request.FILES:
                photo = handle_uploaded_file(
                    request.FILES['photo'],
                    'photos/%s' % request.user.id
                )
                form.instance.photo = photo
            form.save()
            return {'redirect': 'accounts:profile'}
    return {'form': form}


@login_required
@render_to('accounts/pm.html')
def pm(request):
    #_sent = PM.objects.filter(sender=request.user, dbs=False).count()
    #recv = PM.objects.filter(addressee=request.user, dba=False).count()
    #msg = int(_sent) + int(recv)
    form = PMForm()
    return {
        'form': form,
        #'pm_sent': _sent,
        #'pm_recv': recv,
        #'pm_all_count': msg
    }


@login_required
@render_to('accounts/pm_send.html', allow_xhr=True)
def pm_send(request):
    form = PMForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'success': True
            }
    return {'form': form}


@login_required
@render_to('accounts/pm_delete.html', allow_xhr=True)
def pm_delete(request, pk):
    message = get_object_or_404(PM, pk=pk)
    if request.user not in (message.addressee, message.sender):
        raise Http404("hands off")
    if request.user == message.addressee:
        message.dba = True
    elif request.user == message.sender:
        message.dbs = True
    else:
        pass
    if message.dbs and message.dba:
        message.delete()
    else:
        message.save()
    return {'message': message or None, 'success': True}


@login_required
def view_pms(request, outcome=False):
    template = get_skin_template(request.user, 'accounts/pms.html')
    if outcome:
        pm = PM.objects.filter(
            sender=request.user, dbs=False).order_by('-sent')
    else:
        pm = PM.objects.filter(
            addressee=request.user, dba=False
        ).order_by('-sent')
    _pages_ = get_settings(request.user, 'pms_on_page', 50)
    page = request.GET.get('page', 1)
    pm = paginate(pm, page, pages=_pages_)
    return render_to_response(
        template,
        {
            'pms': pm,
            'outcome': outcome,
            'page': pm
        },
        context_instance=RequestContext(
            request,
            processors=[pages]
        )
    )


@login_required
def view_pm(request, pm_id=0):
    template = get_skin_template(request.user, 'accounts/pm.html')
    pm = get_object_or_404(PM, pk=pm_id)
    user = request.user
    if (user.id != pm.sender.id) and (user.id != pm.addressee.id):
        raise Http404("go away")
    if user == pm.addressee:
        pm.is_read = True
        pm.save()
    return render_to_response(
        template,
        {'pmsg': pm},
        context_instance=RequestContext(request)
    )


@login_required
def delete_pm(request, pm_id=0):
    user = request.user
    pm = get_object_or_404(PM, id=pm_id)
    if pm.sender == user:
        if pm.dba:
            pm.delete()
        else:
            pm.dbs = True
            pm.save()
        return redirect('/pm/deleted')
    elif pm.addressee == user:
        if pm.dbs:
            pm.delete()
        else:
            pm.dba = True
            pm.save()
        return redirect('/pm/deleted')

    return redirect('/pm/permissiondenied')


@lock_with_dev({'ALLOW_REGISTER': True})
def onsite_register(request):
    template = get_skin_template(request.user, 'accounts/register.html')
    if request.user.username:
        return redirect('/')
    #old sids deletion
    rsids = RegisterSid.objects.all()
    now = datetime.now()
    for rsid in rsids:
        if rsid.expired < now:
            rsid.delete()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            sid = form.cleaned_data['sid']
            password = form.cleaned_data['password1']
            username = form.cleaned_data['username']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            newuser = User(username=username, email=email, nickname=nickname)
            newuser.set_password(password)
            #a kind of dangerous but ..
            skin = Skin.objects.get(name__iexact='default')
            army = Army.objects.get(name__iexact='none')
            newuser.skin = skin
            newuser.army = army
            #saving before applying some ManyToMany data
            from apps.core.settings import SETTINGS as ONSITE_SETTINGS
            newuser.settings = ONSITE_SETTINGS
            newuser.save()
            #rank
            try:
                newuser_rank = Rank.objects.get(codename='users')
            except Rank.DoesNotExist:
                newuser_rank = Rank.objects.order_by('id')[0]
            newuser.ranks.add(newuser_rank)
            newuser.save()
            try:
                rsid = RegisterSid.objects.get(sid=sid)
                rsid.delete()
            except RegisterSid.DoesNotExist:
                #O_O
                pass
            return redirect('wh:registered')
        else:
            #register denied
            rsids_byip = RegisterSid.objects.filter(
                ip=request.META['REMOTE_ADDR']
            ).count()
            if rsids_byip > 5:
                msg = _(
                    'You\'ve exceeded limit of registration, '
                    'please wait 10 minutes and try again, thank you'
                )
                form._errors['answ'] = ErrorList([msg])
                return render_to_response(
                    template,
                    {'form': form},
                    context_instance=RequestContext(request)
                )

            sid = form.data.get('sid')
            return render_to_response(
                template,
                {
                    'form': form,
                    'sid': sid
                },
                context_instance=RequestContext(request))
    else:
        form = RegisterForm()
        sid = sha1(str(randint(0, 100))).hexdigest()
        while 1:
            sid = sha1(str(randint(0, 100))).hexdigest()
            sids = RegisterSid.objects.filter(sid=sid)
            if not sids:
                break
        form.fields['sid'].initial = sid
        return render_to_response(
            template,
            {
                'form': form,
                'sid': sid
            },
            context_instance=RequestContext(request)
        )


def get_math_image(request, sid=''):
    from PIL import ImageFont
    from PIL import ImageDraw
    #for joke sake
    if not sid:
        image = Image.new('RGBA', (630, 40), (0, 0, 0))
        #print os.path.join(settings.MEDIA_ROOT,'arial.ttf')
        ifo = ImageFont.truetype(os.path.join(settings.MEDIA_ROOT, 'arial.ttf'), 24)
        draw = ImageDraw.Draw(image)
        draw.text((2, 0), 'Hope is the first step on the road to the disappointment', font=ifo)
        img_path = os.path.join(settings.MEDIA_ROOT, 'tmp/bannerimage.png')
        image.save(img_path, 'PNG')
        image = open(img_path).read()
        os.remove(img_path)
        return HttpResponse(image, mimetype='image/png')
    #end for joke sake
    f = 0
    s = 0
    while 1:
        f = randint(10, 98)
        s = randint(2, 9)
        if f % s == 0:
            break
    t = randint(0, 20)
    image = Image.new('RGBA', (95, 40), (0, 0, 0))
    ifo = ImageFont.truetype(os.path.join(settings.MEDIA_ROOT, 'arial.ttf'), 24)
    #print ifo
    draw = ImageDraw.Draw(image)
    draw.text(
        (2, 0),
        str(f) + '/' + str(s) + '-' + str(t),
        font=ifo
    )
    fp_name = '%s/tmp/%s_math_image.png' % (settings.MEDIA_ROOT, str(random())[2:6])
    image.save(fp_name, 'PNG')
    image = open(fp_name, 'r').read()
    os.remove(fp_name)
    answ = f / s - t
    #if sid:
    offset = int(8)
    expired = datetime.now() + timedelta(minutes=offset)
    ip = request.META['REMOTE_ADDR']
    rsid = RegisterSid(sid=sid, expired=expired, ip=ip, value=answ)
    rsid.save()
    return HttpResponse(image, mimetype='image/png')


@login_required
def change_password(request):
    template = get_skin_template(request.user, 'accounts/change_password.html')
    form = PasswordChangeForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            user = request.user
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            return redirect('wh:password-changed')

    return render_to_response(
        template,
        {'form': form},
        context_instance=RequestContext(request)
    )


@render_to('accounts/password_recovery.html')
def password_recover(request):
    form = PasswordRecoverForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            from hashlib import sha1
            from random import random
            new_pass = sha1(str(random())).hexdigest()[4:13]
            u = form.cleaned_data['login']
            email = form.cleaned_data['email']
            user = User.objects.get(username__exact=u)
            user.set_password(new_pass)
            text_content = (
                "Your login name is %s and your "
                "password have changed to %s "
                "Please keep your password with safty, "
                "don't declare it to anyone "
                "even to administration of the resourse."
                "Remember, that administration never request "
                "your password from you."
                "Thank you for using our service."
            ) % (request.user.username, new_pass)
            if settings.SEND_MESSAGES:
                send_mail(
                    'Password Changed',
                    text_content, settings.FROM_EMAIL,
                    [email], fail_silently=False,
                    auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD
                )
            user.save()
            return {'redirect': '/accounts/password/changed/successful'}
    return {'form': form}


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


#@has_permission('wh.can_test')
#x means ajaX
@login_required
def x_get_users_list(request, nick_part=''):
    nick = nick_part or ''
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    if len(nick_part) < 2:
        response.write('[]')
        return response

    users = User.objects.filter(nickname__icontains=nick, is_active=True)
    if users:
        #response.write(serializers.serialize('json',users))
        us = [i.nickname for i in users]
        #simplejson needs
        from simplejson import dumps
        response.write(dumps(us))
    else:
        response.write('[]')
    return response


def get_skins_raw(request, pk):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    try:
        side = Side.objects.get(pk=pk)
        skins = Skin.objects.filter(
            Q(is_general=True) |
            Q(fraction__id__exact=side.fraction.id)
        ).order_by('id')
        response.write(serializers.serialize("json", skins))
    except Side.DoesNotExist:
        #skins = []
        response.write('[failed]')
    return response


#TODO: rewrite
def get_user_avatar(request, nickname=''):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    try:
        user = User.objects.get(nickname__iexact=nickname)
        if user.avatar:
            response.write(user.avatar.read())
        else:
            if hasattr(user.army, 'side'):
                img_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "avatars/%s/default.png" % (user.army.side.name.lower())
                )
            else:
                img_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "avatars/default.png"
                )
            try:
                img = open(img_path, 'rb')
            except IOError:
                img_path = os.path.join(settings.MEDIA_ROOT, 'avatars/none.png')
                img = open(img_path, 'rb')
            response.write(img.read())
    except User.DoesNotExist:
        img_path = os.path.join(settings.MEDIA_ROOT, 'avatars/none.png')
        img = open(img_path, 'rb')
        response.write(img.read())
    return response


def get_race_icon(request, race):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    race = get_object_or_none(Side, name__iexact=race)
    if race:
        img_path = os.path.join(
            settings.MEDIA_ROOT, 'images/armies/50x50/%s.png' % race.name.lower()
        )
    else:
        img_path = os.path.join(
            settings.MEDIA_ROOT, 'images/armies/50x50/none.png'
        )
    try:
        img = open(img_path, 'rb')
    except IOError:
        img_path = os.path.join(
            settings.MEDIA_ROOT, 'images/armies/50x50/none.png'
        )
        img = open(img_path, 'rb')
    response.write(img.read())
    return response


def get_user_side_icon(request, nickname=''):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    try:
        user = User.objects.get(nickname__iexact=nickname)
        if hasattr(user.army, 'side'):
            img_path = os.path.join(
                settings.MEDIA_ROOT,
                'accounts/50x50/%s.png' % user.army.side.name.lower()
            )
            try:
                os.stat(img_path)
            except OSError:
                img_path = os.path.join(
                    settings.MEDIA_ROOT, 'accounts/50x50/none.png'
                )
            img = open(img_path, 'rb')
        else:
            img_path = os.path.join(
                settings.MEDIA_ROOT, 'accounts/50x50/none.png'
            )
            img = open(img_path, 'rb')
        response.write(img.read())
        del img
    except User.DoesNotExist:
        img_path = os.path.join(
            settings.MEDIA_ROOT,
            'accounts/50x50/none.png'
        )
        img = open(img_path, 'rb')
        response.write(img.read())
        del img
    return response


def favicon(request):
    response = HttpResponse()
    response['Content-Type'] = 'image/vnd.microsoft.icon'
    if hasattr(request.user, 'nickname'):
        try:
            file_name = 'images/armies/%s/title_16x16.png' % (request.user.army.side.name.lower())
            #file_path = os.path.join(settings.MEDIA_ROOT,file_name)
            _file = open(os.path.join(settings.MEDIA_ROOT, file_name), 'rb')
        except:
            _file = open(os.path.join(settings.MEDIA_ROOT, 'favicon.ico'), 'rb')
    else:
        _file = open(os.path.join(settings.MEDIA_ROOT, 'favicon.ico'), 'rb')
    response.write(_file.read())
    return response


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


# noinspection PyUnresolvedReferences
@render_to('accounts/password_restore_initiate.html')
def password_restore_initiate(request):
    form = PasswordRestoreInitiateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            users = form.cleaned_data['users']
            #sids = []
            sids = UserSID.objects.filter(user__in=users, expired=True)
            sids = list(sids)
            if not sids:
                for user in users:
                    sid = UserSID.objects.create(user)
                    sids.append(sid)
            else:
                for user in users:
                    sid = UserSID.objects.filter(
                        user=request.user).order_by('-id')[0]
                    sids.append(sid)
                    (lambda x: x)(user)

            for sid in sids:
                msg = settings.PASSWORD_RESTORE_REQUEST_MESSAGE % {
                    'link': settings.DOMAIN + "%s" % reverse(
                    'wh:password-restore', args=(sid.sid, ))
                }
                if settings.SEND_MESSAGES:
                    send_mail(
                        subject=unicode(
                            _('Your password requested to change')
                        ),
                        message=unicode(msg),
                        from_email=settings.FROM_EMAIL,
                        recipient_list=[sid.user.email]
                    )
            return {'redirect': 'core:password-restore-initiated'}
    return {'form': form}


@prevent_bruteforce
@render_to('accounts/password_restore.html')
def password_restore(request, sid):
    instance = get_object_or_None(UserSID, sid=sid, expired=False)
    if not instance:
        request.session['brute_force_iter'] \
            = request.session.get('brute_force_iter', 0) + 1
        raise Http404("not found")

    form = PasswordRestoreForm(
        request.POST or None, instance=instance, request=request
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {'redirect': 'core:password-restored'}
    return {'form': form}
