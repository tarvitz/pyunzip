# Create your views here.
# ^^, coding: utf-8 ^^,
#from settings import MEDIA_ROOT,FROM_EMAIL
from django.conf import settings
from apps.wh.models import Side,Army,PM,RegisterSid, WishList, Skin,Rank, User, \
    Rank,MiniQuote
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseServerError
from django.template import RequestContext
from django.shortcuts import render_to_response,get_object_or_404
from django.contrib import auth
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from apps.core.decorators import has_permission, lock_with_dev
#from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, InvalidPage
from django.core import serializers
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.core.mail import send_mail
from django.forms.util import ErrorList
from apps.wh.forms import UploadAvatarForm, UpdateProfileForm, UpdateProfileModelForm, \
    PMForm, RegisterForm, AddWishForm,PasswordChangeForm, PasswordRecoverForm, LoginForm
from apps.core import make_links_from_pages as make_links
from apps.core import pages, get_skin_template
from cStringIO import StringIO
import Image
from datetime import datetime,timedelta
from hashlib import sha1
from random import randint, random
from django.template import Template,Context
#filters
from apps.news.templatetags.newsfilters import spadvfilter
from django.template.defaultfilters import striptags
#from django.views.generic.simple import direct_to_template
from apps.core.shortcuts import direct_to_template
from apps.core.helpers import get_settings, get_object_or_none, paginate, can_act, \
    handle_uploaded_file, render_to
import os

#decorators
def superuser_required(func,*args,**kwargs):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_superuser:
            return func(*args,**kwargs)
        else:
            return HttpResponseRedirect('/permission/denied')
    return wrapper

#endofdecorators

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
            return {'redirect': '/'}
    return {'form': form}

#KIND A HACK o_O
@superuser_required
def sulogin(request):
    referer = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            superuser = auth.authenticate(username='banned',password='banned')
            setattr(user,'backend',superuser.backend)
            auth.login(request,user)
            return HttpResponseRedirect('/')
        except User.DoesNotExist:
            return render_to_response('accounts/login', {'errors': True,
                'next':referer,'referer':referer},
                context_instance=RequestContext(request))
    return render_to_response('accounts/login.html', {'next': referer,'referer':referer},
    context_instance=RequestContext(request))

def logout(request):
    if hasattr(request.user,'useractivity'):
        request.user.useractivity.is_logout = True #do not display users whom logged out
        request.user.useractivity.save()
    auth.logout(request)
    return HttpResponseRedirect('/')
    #return render_to_response('accounts/logout.html',{},
    #    context_instance=RequestContext(request))

#Поиск по имени рега
#Переписать все это нахуй, стремно как-то выглядит
#upd: 06.10.2010 - внатуре, сижу ржу над топорностью, надо бы переписать и вправду
@login_required
def profile(request,account_name='self'):
    template = get_skin_template(request.user,'accounts/profile.html')
    if account_name == 'self':
        from apps.files.models import Gallery
        #galleries = Gallery.objects.filter(owner=request.user)
        return render_to_response(template,
            {'usr': request.user,
            '__galleries':'#'}, #still not implemented
            context_instance=RequestContext(request))
    try:
        user = User.objects.get(username__exact=account_name)
        permissions = user.user_permissions.all()
    except User.DoesNotExist:
        user = {'errors':_('There is no such user')}
        permissions = {}
    return render_to_response(template,
        {'usr': user,
        'userperms': permissions},
        context_instance=RequestContext(request))

#Поиск по имени ника
@login_required
def profile_by_nick(request, nickname ='self'):
    template = get_skin_template(request.user, 'accounts/profile.html')
    from apps.files.models import Gallery
    if nickname == 'self':
        galleries = Gallery.objects.filter()
        return render_to_response('accounts/profile.html',
            {'usr': request.user,
            'galleries':galleries},
            context_instance=RequestContext(request))
    try:
        user = User.objects.get(nickname__exact=nickname)
        galleries = Gallery.objects.filter()
        if not user.is_active:
            return HttpResponseRedirect('/user/does/not/exist')
    except    User.DoesNotExist:
            return HttpResponseRedirect('/user/does/not/exist')
    
    if hasattr(user,'user_permissions'): 
        permissions = user.user_permissions.all()
    else:
        permissions = dict()
        
    return render_to_response(template,
        {'usr': user,
        'userperms': permissions,
        'galleries': galleries},
        context_instance=RequestContext(request))

#Все пользователи
@login_required
def users(request):
    template = get_skin_template(request.user,'accounts/index.html')
    page = request.GET.get('page',1)
    users = User.objects.filter(is_active=True).order_by('date_joined')
    _pages_ = get_settings(request.user,'objects_on_page',30)
    #paginator = Paginator(users, _pages_)
    #try:
    #    users = paginator.page(page)
    #    paginator.number = int(page)
    #except (InvalidPage ,EmptyPage):
    #    users = paginator.page(1)
    #    paginator.number = page(1)
    users = paginate(users,page,pages=_pages_)
    return render_to_response(template,
        {'users':users,
        'page':users},
        context_instance=RequestContext(request))

#CLEANUP:
@login_required
def upload_avatar(request):
    template = get_skin_template(request.user,'test/upload_avatar.html')
    if request.method == 'POST':
        form = UploadAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            #avatar_data = request.FILES['avatar']
            avatar_data = form.cleaned_data['avatar']
            file = ''
            for i in avatar_data.chunks():
                file += i
            avatar = Image.open(StringIO(file))
            #print "%s/temp/avatar_%s.jpg" % (MEDIA_ROOT,request.user.id)
            avatar.save("%s/temp/avatar_%s.jpg" % (MEDIA_ROOT,request.user.id))
            return HttpResponseRedirect('/upload/successfull')
        else:
            return render_to_response(template,
                {'form': form,},
                context_instance=RequestContext(request))
    form = UploadAvatarForm()
    return render_to_response(template,
        {'form': form},
        context_instance=RequestContext(request))

@login_required
def update_profile(request):
    template = get_skin_template(request.user, 'accounts/update_profile.html')
    if request.method == 'POST':
        form = UpdateProfileModelForm(request.POST, request.FILES, instance=request.user, request=request)
        if form.is_valid():
            if 'avatar' in request.FILES:
                avatar = handle_uploaded_file(request.FILES['avatar'],
                    'avatars/%s' % request.user.id)
                form.instance.avatar = avatar
            if 'photo' in request.FILES:
                photo = handle_uploaded_file(request.FILES['photo'],
                    'photos/%s' % request.user.id)
                form.instance.photo = photo
            form.save()
            return HttpResponseRedirect(reverse('wh:profile'))
        else:
            return direct_to_template(request, template,
                {'form': form})
    form = UpdateProfileModelForm(instance=request.user, request=request)
    return direct_to_template(request, template, {'form': form})

@login_required
def update_profile_old(request):
    template = get_skin_template(request.user, 'accounts/update_profile_old.html')
    sides = Side.objects.all().order_by('id')
    armies = Army.objects.all()
    sides_list = []
    jlist = []
    for side in sides:
        for army in armies:
            if army.side.id == side.id: jlist.append('armies[%s][%s]="%s";' % (side.id,army.id,army.name))

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            from PIL import Image
            u = User.objects.get(id__exact=request.user.id)
            avatar_data = form.cleaned_data['avatar']
            photo_data = form.cleaned_data['photo']
            if avatar_data:
                avatar_file = ''
                for i in avatar_data.chunks(): avatar_file += i
                avatar = Image.open(StringIO(avatar_file))
                avatar_path = "%s/avatars/avatar_%s.%s" % (settings.MEDIA_ROOT,request.user.id,
                    avatar_data.name[avatar_data.name.rindex('.')+1:] )
                avatar.save(avatar_path)
                avatar_path = avatar_path[len(settings.MEDIA_ROOT):]
                if avatar_path[0] == '/': avatar_path = avatar_path[1:]
                u.plain_avatar = avatar_path
            if photo_data:
                photo_file = ''
                for i in photo_data.chunks(): photo_file += i
                photo = Image.open(StringIO(photo_file))
                photo_path = "%s/photos/photo_%s.%s" % (settings.MEDIA_ROOT, request.user.id,
                    photo_data.name[photo_data.name.rindex('.')+1:] )
                photo.save(photo_path)
                photo_path = photo_path[len(settings.MEDIA_ROOT):]
                if photo_path[0] == '/': photo_path = photo_path[1:]
                u.photo = photo_path
            #nickname = form.cleaned_data['nickname']
            #if not nickname: nickname = u.nickname
            #if nickname: u.nickname = nickname
            army = request.POST.get('army','')
            if not army: army = u.army.id
            try:
                a = Army.objects.get(id__exact=army)
            except Army.DoesNotExist:
                a = Army.objects.all()[0]
            old_army = u.army
            u.army = a
            #jid = form.cleaned_data['jid']
            #uin = form.cleaned_data['uin']
            #gender = form.cleaned_data['gender']
            #if jid: u.jid = jid
            #if uin: u.uin = uin
            #автоматический финт
            skin = Skin.objects.get(id=int(form.cleaned_data['skin']))
            u.skin = skin
            keys = ['about','email','jid','uin', 'gender','nickname','first_name','last_name']
            for key in keys:
                if form.cleaned_data[key]: setattr(u,key,form.cleaned_data[key])
            #make avatar from army image and plain_avatar
            if old_army != u.army or not u.avatar:
                import Image
                from math import trunc
                army_img = os.path.join(settings.MEDIA_ROOT,'images/armies/%s/%s_16x16.png' % (u.army.side.name.lower(), u.army.name.lower()))
                #TODO MAKE A REVERTION
                #print army_img 
            u.save()
            #return HttpResponseRedirect('/accounts/update/profile/successfull')
            return HttpResponseRedirect('/accounts/update/profile/') #flip it back
        else:
            return render_to_response(template,
                {'form': form ,
                'sides':sides,
                'armies':armies,
                'armies_list': jlist},
                context_instance=RequestContext(request))
    form = UpdateProfileForm()
    keys = ['about','email','jid','uin','gender', 'nickname','first_name','last_name']
    for key in keys:
        form.fields[key].initial = getattr(request.user,key)
    return render_to_response(template,
        {'form':form,
        'sides':sides,
        'armies':armies,
        'armies_list': jlist},
        context_instance=RequestContext(request))

@login_required
def armies_list(request):
    template = get_skin_template(request.user, 'test/armies.html')
    sides = Side.objects.all().order_by('id')
    armies = Army.objects.all()
    sides_list = []
    jlist = []
    for side in sides:
        for army in armies:
            if army.side.id == side.id: jlist.append('armies[%s][%s]="%s";' % (side.id,army.id,army.name))
    return render_to_response(template,
        {'sides':sides,
        'armies': armies,
        'armies_list': jlist},
        context_instance=RequestContext(request))

@login_required
def pm_view(request):
    template = get_skin_template(request.user, 'pm.html')
    user = request.user
    sent = PM.objects.filter(sender=user,dbs=False).count()
    recv = PM.objects.filter(addressee=user,dba=False).count()
    all = int(sent)+int(recv)
    return render_to_response(template,
        {'pm_sent': sent,
        'pm_recv': recv,
        'pm_all': all},
        context_instance=RequestContext(request))

@login_required
@can_act
def send_pm(request,nickname=''):
    template = get_skin_template(request.user, 'accounts/send_pm.html')
    if request.method == 'POST':
        form = PMForm(request.POST, request=request)
        if form.is_valid():
            sender = request.user
            addressee = form.cleaned_data['addressee']
            a = User.objects.get(nickname=addressee)
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            now = datetime.now()
            sender_chk_limit = PM.objects.filter(sender=sender,dbs=False).count()
            if int(sender_chk_limit) > 100:
                return HttpResponseRedirect('/pm/send/senderlimiterror')
            addr_chk_limit = PM.objects.filter(addressee=a,dba=False).count()
            if int(addr_chk_limit) > 100:
                return HttpResponseRedirect('/pm/send/addresseelimiterror')
            pm = PM(sender=sender,addressee=a,title=title,content=content,sent=now)
            pm.save()
            #send notification here
            return HttpResponseRedirect('/pm/send/successfull')
        else:
            return render_to_response(template,
                {'form': form,},
                context_instance=RequestContext(request))
    else:
        form = PMForm()
        if nickname: form.fields['addressee'].initial = nickname
        return render_to_response(template,
            {'form': form,},
            context_instance=RequestContext(request))

@login_required
def view_pms(request,outcome=False):
    template = get_skin_template(request.user, 'accounts/pms.html')
    if outcome == True:
        pm = PM.objects.filter(sender=request.user,dbs=False).order_by('-sent')
    else:
        pm = PM.objects.filter(addressee=request.user,dba=False).order_by('-sent')
    _pages_ = get_settings(request.user,'pms_on_page',50)
    page = request.GET.get('page',1)
    pm = paginate(pm,page,pages=_pages_)
    return render_to_response(template,
        {'pms': pm,
        'outcome': outcome,
        'page': pm},
        context_instance=RequestContext(request,
            processors=[pages]))
@login_required
def view_pm(request,pm_id=0):
    template = get_skin_template(request.user, 'accounts/pm.html')
    try:
        pm = PM.objects.get(id=pm_id)
    except PM.DoesNotExist:
        return HttpResponseRedirect('/pm/doesnotexist')
    user = request.user
    if (user.id != pm.sender.id) and (user.id != pm.addressee.id):
        return HttpResponseRedirect('/pm/doesnotexist')
    if user == pm.addressee:
        pm.is_read = True
        pm.save()
    return render_to_response(template,
        {'pmsg': pm },
        context_instance=RequestContext(request))

@login_required
def delete_pm(request,pm_id=0, approve='force'):
    user = request.user
    try:
        pm = PM.objects.get(id=pm_id)
        if pm.sender == user:
            if pm.dba:
                pm.delete()
            else: 
                pm.dbs = True
                pm.save()
            return HttpResponseRedirect('/pm/deleted')
        elif pm.addressee == user:
            if pm.dbs: 
                pm.delete()
            else:
                pm.dba = True
                pm.save()
            return HttpResponseRedirect('/pm/deleted')
        else:
            return HttpResponseRedirect('/pm/permissiondenied')
    except:
        HttpResponseRedirect('/pm/doesnotexist')

@lock_with_dev({'ALLOW_REGISTER': True})
def onsite_register(request):
    template = get_skin_template(request.user,'accounts/register.html')
    if request.user.username:
        return HttpResponseRedirect('/')
    #old sids deletion
    rsids = RegisterSid.objects.all()
    now = datetime.now()
    for rsid in rsids:
        if rsid.expired<now: rsid.delete()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            sid = form.cleaned_data['sid']
            password = form.cleaned_data['password1']
            username = form.cleaned_data['username']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            newuser = User(username=username,email=email,nickname=nickname)
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
            return HttpResponseRedirect('/registered')
        else:
            #register denied
            rsids_byip = RegisterSid.objects.filter(ip=request.META['REMOTE_ADDR']).count()
            if rsids_byip>5:
                msg = _('You\'ve exceeded limit of registration, please wait 10 minutes and try again, thank you')
                form._errors['answ'] = ErrorList([msg])
                return render_to_response(template,
                    {'form': form},
                    context_instance=RequestContext(request))

            sid = form.data.get('sid')
            return render_to_response(template,
                {'form': form,
                'sid': sid},
                context_instance=RequestContext(request))
    else:
        form = RegisterForm()
        while 1:
            sid = sha1(str(randint(0,100))).hexdigest()
            sids = RegisterSid.objects.filter(sid=sid)
            if not sids: break
        form.fields['sid'].initial = sid
        return render_to_response(template,
            {'form': form,
            'sid': sid},
            context_instance=RequestContext(request))
    
def get_math_image(request,sid=''):
    import ImageFont, ImageDraw
    #for joke sake
    if not sid:
        image = Image.new('RGBA', (630,40),(0,0,0))
        #print os.path.join(settings.MEDIA_ROOT,'arial.ttf')
        ifo = ImageFont.truetype(os.path.join(settings.MEDIA_ROOT,'arial.ttf'), 24)
        draw = ImageDraw.Draw(image)
        draw.text((2,0), 'Hope is the first step on the road to the disappointment', font=ifo)
        img_path = os.path.join(settings.MEDIA_ROOT,'tmp/bannerimage.png')
        image.save(img_path,'PNG')
        image = open(img_path).read()
        os.remove(img_path)
        return HttpResponse(image, mimetype='image/png')
    #end for joke sake
    while 1:
        f = randint(10,98)
        s = randint(2,9)
        if f % s == 0: break
    t = randint(0,20)
    image = Image.new('RGBA',(95,40),(0,0,0))
    ifo = ImageFont.truetype(os.path.join(settings.MEDIA_ROOT,'arial.ttf'), 24)
    #print ifo
    draw = ImageDraw.Draw(image)
    draw.text((2, 0), str(f)+'/'+str(s)+'-'+str(t), font=ifo)
    fp_name = '%s/tmp/%s_math_image.png' % (settings.MEDIA_ROOT, str(random())[2:6])
    image.save(fp_name, 'PNG')
    image = open(fp_name,'r').read()
    os.remove(fp_name)
    answ = f/s-t
    #if sid:
    offset = int(8)
    expired = datetime.now() + timedelta(minutes=offset)
    ip = request.META['REMOTE_ADDR']
    rsid = RegisterSid(sid=sid, expired=expired, ip=ip, value=answ)
    rsid.save()
    return HttpResponse(image, mimetype='image/png')

#OBSOLETE, delete when it's possible
def view_wish_list(request):
    template = get_skin_template(request.user,'feedback/wishes.html')
    try:
        page = request.GET.get('p',1)
    except:
        page = 1 
    if request.user.is_superuser: wishes = WishList.objects.filter()
    else: wishes = WishList.objects.filter(published=True)
    _pages_ = get_settings(request.user,'objects_on_page',30)
    paginator = Paginator(wishes,_pages_)
    try:
        wishes = paginator.page(page)
        paginator.number = int(page)
    except (EmptyPage, InvalidPage):
        wishes = paginator.page(1)
        paginator.number = int(1)
    #links = make_links(paginator.num_pages)
    links = paginator.page_range
    return render_to_response(template,
        {'wishes': wishes,
        'links': links,
        'page': paginator},
        context_instance=RequestContext(request,
            processors=[pages]))

#realize anonymous possibilities
@login_required
@can_act
def add_wish(request):
    template = get_skin_template(request.user,'feedback/add_wish.html')
    if request.method == 'POST':
        form = AddWishForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data['post']
            #Here we shoud insert user check uping' if he is not Anonymous
            author = request.user
            ip = request.META['REMOTE_ADDR']
            published = False
            wish = WishList(post=post, author=author, ip=ip, published=published)
            wish.save()
            return HttpResponseRedirect('/feedback/wishes/added')

        else:
            return render_to_response(template,
            {'form': form},
            context_instance=RequestContext(request))
    else:
        form = AddWishForm()
        return render_to_response(template,
            {'form': form},
            context_instance=RequestContext(request))
@login_required
def manage_wish(request,wish_id,filter=''):
    #FIXME: add this ability to coders squad
    if request.user.is_superuser:
        try:
            wish = WishList.objects.get(id=wish_id)
            if filter == 'approve':
                wish.approved = True
                wish.published = True
                wish.save()
                return HttpResponseRedirect('../../')
            elif filter == 'publish':
                wish.published = True
                wish.save()
                return HttpResponseRedirect('../../')
            elif filter == 'unpublish':
                wish.published = False
                wish.save()
                return HttpResponseRedirect('../../')
            elif filter == 'unapprove':
                wish.approved = False
                wish.save()
                return HttpResponseRedirect('../../')
            elif filter == 'done':
                wish.delete()
                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('/feedback/wishes')
        except WishList.DoesNotExist:
            return HttpRedirect('/feedback/wishes')
    else:
        return HttpRedirect('/feedback/wishes')
@login_required
def change_password(request):
    template = get_skin_template(request.user,'accounts/change_password.html')
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST,request=request)
        if form.is_valid():
            user = request.user
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            return HttpResponseRedirect('/accounts/password/changed/successful')
        else:
            return render_to_response(template,
                {'form': form },
                context_instance=RequestContext(request))
    else:
        form = PasswordChangeForm(request=request)
        return render_to_response(template,
            {'form': form},
            context_instance=RequestContext(request))

def password_recover(request):
    template = get_skin_template(request.user,'accounts/password_recovery.html')
    if request.method == 'POST':
        form = PasswordRecoverForm(request.POST, request=request)
        if form.is_valid():
            from hashlib import sha1
            from random import random
            new_pass = sha1(str(random())).hexdigest()[4:13]
            u = form.cleaned_data['login']
            email = form.cleaned_data['email']
            user = User.objects.get(username__exact=u)
            user.set_password(new_pass)
            text_content = """
Your login name is %s and 
your password have changed to %s
Please keep your password with safty, don't declare it to anyone
even to administration of the resourse.
Remember, that administration never request your password from you.

Thank you for using our service.""" % (request.user.username,new_pass)
            send_mail('Password Changed', text_content, settings.FROM_EMAIL,
                [email], fail_silently=False,
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD)
            user.save()
            return HttpResponseRedirect('/accounts/password/changed/successful')
        else:
            return render_to_response(template,
                {'form': form},
                context_instance=RequestContext(request))
    else:
        form = PasswordRecoverForm()
        return render_to_response(template,
            {'form': form},
            context_instance=RequestContext(request))

def show_rank(request,id=None,codename=None):
    if id is None and codename is None:
        return HttpResponseRedirect('/')
    template = get_skin_template(request.user,'ranks/rank.html')
    try:
        if codename:
            rank = Rank.objects.get(codename__exact=codename)
        elif id:
            rank = Rank.objects.get(id=id)
        img = "%s/images/ranks/%s/%s.jpg" % (settings.MEDIA_ROOT,rank.type.type.lower(),rank.codename)
        from os import stat
        try:
            stat(img)
            img = "images/ranks/%s/%s.jpg" % (rank.type.type.lower(), rank.codename)
        except OSError:
            img = "images/ranks/_none_.jpg" 
    except:
        return HttpResponseRedirect('/')
    return render_to_response(template,
        {'rank':rank,
        'img': img},
        context_instance=RequestContext(request))

#implement unification method to edit simple text fields within ONE function
@login_required
@can_act
def edit_rank(request,codename=None,id=None):
    try:
        rank = Rank.objects.get(codename__exact=codename)
    except Rank.DoesNotExist:
        error_msg = u"Rank not found"
        return HttpResponseServerError(error_msg)
    #insert perms
    if request.method == 'POST':
        post = request.POST.copy()
        if post.has_key('text'):
            if rank.description != post['text']:
                rank.description = post['text']
            #insert DDoS prevention
            rank.save()
            html = Template("[success]")
            html = html.render(Context({}))
            response = HttpResponse(html)
            response['Content-Type'] = "text/javascript"
            return response
        else:
            error_msg = u"Unknown data is submitted"
            return HttpResponseServerError(error_msg)
    else:
        error_msg = u"no POST data is sent"
        return HttpResponseServerError(error_msg)

def get_rank(request,codename=None,id=None,raw=True):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        rank = Rank.objects.get(codename__exact=codename)
        #FIXME :(
        from time import sleep
        sleep(0.125)
        if not raw:
            rank.description = striptags(rank.description)
            rank.description = spadvfilter(rank.description)
        response.write(serializers.serialize("json",[rank]))
        return response
    except Rank.DoesNotExist:
        msg_error = u"no rank"
        return HttpResponseServerError(msg_error)

#@has_permission('wh.can_test')                
#x means ajaX
@login_required
def x_get_users_list(request,nick_part=''):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    if len(nick_part)<2:
    	response.write('[]')
   	return response
    users = User.objects.filter(nickname__icontains=nick_part,is_active=True)
    if users:
        #response.write(serializers.serialize('json',users))
        us = [i.nickname for i in users]
        #simplejson needs
        from simplejson import dumps
        response.write(dumps(us))
    else:
        response.write('[]')
    return response

#CLEANUP:
def urls_parse(request):
    template = get_skin_template(request.user, 'test/urls_parse.html')
    from urls import urlpatterns as urls
    return render_to_response(template,
        {'urls': urls,
        'path': request.path},
        context_instance=RequestContext(request))

def get_miniquote_raw(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        mq = MiniQuote.objects.order_by('?')[0]
    except IndexError:
        response.write('false')
        return response
    response.write(serializers.serialize("json",[mq]))
    
    return response

def xhr_get_armies(request, id=None):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    if not id:
        response.write("[]")
        return response
    armies = Army.objects.filter(side__id=id)
    response.write(serializers.serialize("json", armies))
    return response

#deprecated, cleanse as soon as possible
def get_armies_raw(request,id):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        armies = Army.objects.filter(side__id__exact=int(id))
        response.write(serializers.serialize("json",armies))
    except Army.DoesNotExist:
        response.write('[failed]')
    return response

def get_skins_raw(request,id):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        side = Side.objects.get(id=id)
        #skins = Skin.objects.filter(Q(name__iexact='default')|Q(fraction__id__exact=side.fraction.id)).order_by('id')
        skins = Skin.objects.filter(Q(is_general=True)|Q(fraction__id__exact=side.fraction.id)).order_by('id')
        response.write(serializers.serialize("json",skins))
    except Side.DoesNotExist:
        #skins = []
        response.write('[failed]')
    return response

def get_user_avatar(request, nickname=''):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    try:
        user = User.objects.get(nickname__iexact=nickname)
        if user.avatar:
            response.write(user.avatar.read())
        else:
            if hasattr(user.army,'side'):
                img_path = os.path.join(settings.MEDIA_ROOT,"avatars/%s/default.png" % (user.army.side.name.lower()))
            else:
                img_path = os.path.join(settings.MEDIA_ROOT,"avatars/default.png")
            try:
                img = open(img_path,'rb')
            except IOError:
                img_path = os.path.join(settings.MEDIA_ROOT,'avatars/none.png')
                img = open(img_path,'rb')
            response.write(img.read())
    except User.DoesNotExist:
        img_path = os.path.join(settings.MEDIA_ROOT,'avatars/none.png')
        img = open(img_path,'rb')
        response.write(img.read())
    return response

def get_user_photo(request,nickname):
    response = HttpResponse()
    response['Content-Type'] = 'image/jpeg'
    user = get_object_or_404(User,nickname__iexact=nickname)
    if user.photo:
        response.write(user.photo.read())
        return response
    else:
        reponse = HttpResponse()
        response['Content-Type'] = 'text/plain'
        response.write('no photo ;)')
        return response

def get_race_icon(request,race):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    race = get_object_or_none(Side,name__iexact=race)
    if race:
        img_path = os.path.join(settings.MEDIA_ROOT,'images/armies/50x50/%s.png' % race.name.lower())
    else:
        img_path = os.path.join(settings.MEDIA_ROOT,'images/armies/50x50/none.png')
    try:
        img = open(img_path,'rb')
    except IOError:
        img_path = os.path.join(settings.MEDIA_ROOT,'images/armies/50x50/none.png')
        img = open(img_path, 'rb')
    response.write(img.read())
    return response

def get_user_side_icon(request,nickname=''):
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    try:
        user = User.objects.get(nickname__iexact=nickname)
        if hasattr(user.army,'side'):
            img_path = os.path.join(settings.MEDIA_ROOT,'accounts/50x50/%s.png' % user.army.side.name.lower())
            try:
                os.stat(img_path)
            except OSError:
                img_path = os.path.join(settings.MEDIA_ROOT,'accounts/50x50/none.png')
            img = open(img_path,'rb')
        else:
            img_path = os.path.join(settings.MEDIA_ROOT,'accounts/50x50/none.png')
            img = open(img_path,'rb')
        response.write(img.read())
        del img
    except User.DoesNotExist:
        img_path = os.path.join(settings.MEDIA_ROOT,'accounts/50x50/none.png')
        img = open(img_path,'rb')
        response.write(img.read())
        del img
    return response

def favicon(request):
    response = HttpResponse()
    response['Content-Type'] = 'image/vnd.microsoft.icon'
    if hasattr(request.user,'nickname'):
        try:
            file_name = 'images/armies/%s/title_16x16.png' % (request.user.army.side.name.lower())
            file_path = os.path.join(settings.MEDIA_ROOT,file_name)
            file = open(os.path.join(settings.MEDIA_ROOT,file_name),'rb')
        except:
            file = open(os.path.join(settings.MEDIA_ROOT,'favicon.ico'),'rb')
    else:
        file = open(os.path.join(settings.MEDIA_ROOT,'favicon.ico'),'rb')
    response.write(file.read())
    return response

@has_permission('wh.set_warnings')
@can_act
def alter_warning(request,nickname,type):
    """alter_warning could increase or decrease warning level of the user """
    from apps.wh.models import Warning,WarningType
    user = get_object_or_404(User,nickname__iexact=nickname)
    warnings = Warning.objects.filter(user__nickname__iexact=nickname)
    if type in 'increase': type_offset = 1
    if type in 'decrease': type_offset = -1
    if warnings:
        #fixing instabillity
        if len(warnings)>1:
            for n in xrange(1,len(warnings)-1):
                #Instabillity
                warnings[n].remove()
        old_warning = warnings[0]
        #FIXME: we should use more strict expired schema
        from datetime import datetime,timedelta
        expired = datetime.now()+timedelta(days=int(old_warning.level)*7)
        new_warning = Warning(user=user,level=int(old_warning.level)+type_offset,expired=expired,style='color:red;')
        #search for a type
        #NOTICE that block could be dangerous because there could not be nor general warningtype nor common!
        if type in 'decrease' and int(old_warning.level) == 1:
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.comments.models import Comment
            ct = ContentType.objects.get(app_label='wh',model='warning')
            try:
                comments = Comment.objects.filter(content_type=ct,object_pk=str(old_warning.pk))
                if comments:
		    for c in comments: c.delete()
            except Comment.DoesNotExist:
                #do nothing
                pass
            old_warning.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        try:
            warning_type = WarningType.objects.get(side=user.army.side,level=int(old_warning.level)+type_offset)
        except WarningType.DoesNotExist:
            try:
                warning_type = WarningType.objects.get(level=int(old_warning.level)+type_offset,is_general=True)
            except WarningType.DoesNotExist:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        
        new_warning.type = warning_type
        new_warning.save()
    else:
        #we can not decreese null warnings :)
        if type in 'decrease':
            return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        #there is no warnings
        try:
            #common_warning contains warning message for each side
            warning_type = WarningType.objects.get(side=user.army.side,level=1)
        except WarningType.DoesNotExist:
            #we fail, so we search for general warning, JUST FOR ALL
            warning_type = WarningType.objects.get(level=1,is_general=True)
        from datetime import datetime,timedelta
        expired = datetime.now()+timedelta(days=7)
        warning = Warning(type=warning_type,user=user,level=1,style='color:red;',expired=expired)
        warning.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@has_permission('wh.set_warnings')
@can_act
def alter_warning_form(request,nickname):
    #implement here an free warning alteration
    from apps.wh.models import Warning,WarningType
    template = get_skin_template(request.user,'warnings/alter.html')
    from apps.wh.forms import WarningForm
    warn_user = get_object_or_404(User,nickname__iexact=nickname)
    if request.method == 'POST':
        form = WarningForm(request.POST,request=request)
        if form.is_valid():
            level = int(form.cleaned_data['level'])
            comment = form.cleaned_data['comment']
            nickname = form.cleaned_data['nickname']
            referer = form.cleaned_data['next']
            try:
                warning_type = WarningType.objects.get(side=warn_user.army.side,level=level)
            except WarningType.DoesNotExist:
                #it's a little bit dangerous
                warning_type = WarningType.objects.get(is_general=True,level=level)
            expired = datetime.now()+timedelta(days=level*7)
            warning = Warning(type=warning_type,user=warn_user,level=level,expired=expired,style='color: red;')
            warning.save()
            if comment:
                #saving comment for warning alteration
                from django.contrib.contenttypes.models import ContentType
                from django.contrib.comments.models import Comment
                ct = ContentType.objects.get(app_label='wh',model='warning')
                c = Comment(content_type=ct,object_pk=str(warning.pk),user=request.user,
                    comment=comment,submit_date=datetime.now(),is_public=True,site_id=1)
                c.save()
            return HttpResponseRedirect(referer)   
        else:
            return direct_to_template(request,template,{'form':form})
    else:
        try:
            warning = Warning.objects.get(user=warn_user)
            level = int(warning.level)
        except Warning.DoesNotExist:
            level = 1
        form = WarningForm(request=request)
        form.fields['level'].initial = level
        form.fields['nickname'].initial = warn_user.nickname
        form.fields['next'].initial = request.META.get('HTTP_REFERER','/')
    return direct_to_template(request,template,{'form':form})

