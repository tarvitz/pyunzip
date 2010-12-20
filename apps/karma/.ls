# Create your views here.
from django.http import HttpResponseRedirect
from apps.core.decorators import null_function
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from apps.core import get_skin_template
from apps.karma.models import Karma,KarmaStatus
from django.contrib.auth.models import User
from apps.karma.forms import AlterKarmaForm
from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.core.paginator import EmptyPage,InvalidPage
from datetime import datetime
from apps.karma.decorators import day_expired
from random import randint
from apps.karma.helpers import check_fraction
from apps.core.helpers import get_settings
from django.conf import settings

@null_function
def up(request):
    pass
    #referer = request.META.get('HTTP_REFERER','/')
    #return HttpResponseRedirect(referer)

@null_function
def down(request):
    pass
    #referer = request.META.get('HTTP_REFERER','/')
    #return HttpResponseRedirect(referer)

@day_expired
def alter_karma(request,choice=None,nickname=None):
    #choice may be up|down
    template = get_skin_template(request,'alter_karma.html')
    alter_status_template = get_skin_template(request,'alter_status.html')
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

            fraction_ident = check_fraction(user,voter)
                
            if fraction_ident:
                k = Karma(user=user,voter=voter,comment=comment,date=now,value=value,url=url)
                k.save()
            #dangers of warp ;) 75% to fail karma's alter
            else:
                if randint(1,100)>=75: #75
                    #20% chance to alter karma with overside value
                    if randint(1,100)>=80:  
                        comment = comment + " [warp's instability]"
                        k = Karma(user=user,voter=voter,comment=comment,date=now,value=value*-1,url=url)
                    else:
                        k = Karma(user=user,voter=voter,comment=comment,date=now,value=value,url=url)
                    k.save()
                    return HttpResponseRedirect(referer)
                    #bad idea ? :)
                    #direct_to_template(request,alter_status_template,{'alter_status':True})
                else:
                    #failed! ;)
                    k = Karma(user=user,voter=voter,comment=comment,date=now,value=0,url=url)
                    k.save()
                    return direct_to_template(request,
                            alter_status_template,{'alter_status':False})
            return HttpResponseRedirect(referer)
        else:
            return direct_to_template(request,template,{'form':form})
    else:
        form = AlterKarmaForm()
        form.fields['hidden_nickname'].initial = nickname
        referer = request.META.get('HTTP_REFERER','/')
        form.fields['referer'].initial = referer
        #MAY BE there is more simple and clear way to capture URL where we got karma ups/downs
        url = referer.replace('://','')
        form.fields['url'].initial = url[url.index('/'):]
        return direct_to_template(request,template,{'form':form})

def show_karma(request,user=None,type='',group=False):
    template = get_skin_template(request.user,'karma.html')
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
    show_null = get_settings(request.user,'show_null_karma',True)
    show_self_null = get_settings(request.user,'show_self_null_karma',True)
    if user is not None:
        if not show_null:
            karmas = karmas.exclude(value=0)
    else:
        if not show_self_null:
            karmas = karmas.exclude(value=0)
    if group:
        pass    
    _pages_ = get_settings(request.user,'karmas_on_page',50) 
    paginator = Paginator(karmas,_pages_)
    try:
        page = request.GET.get('page',1)
        karmas = paginator.page(page)
        karmas.number = int(page)
    except (InvalidPage,EmptyPage):
        karmas = paginator.page(1)
        karmas.number = 1
    return direct_to_template(request,template,{'karmas':karmas,'page':karmas})

def show_karmastatus_description(request,id=None,codename=None):
    if id is None and codename is None:
        return HttpResponseRedirect('/')
    template = get_skin_template(request.user,'karma/description.html')
    try:
        if codename:
            status = KarmaStatus.objects.get(codename__iexact=codename)
        elif id:
            status = KarmaStatus.objects.get(id=id)
        img = "%s/images/karma/status/%s.jpg" % (settings.MEDIA_ROOT,status.codename)
        from os import stat
        try:
            stat(img)
            img = "images/karma/status/%s.jpg" % (status.codename)
        except OSError:
            img = "images/karma/status/_none_" 
    except:
            return HttpResponseRedirect('/')
    return direct_to_template(request,template,
        {'status':status,
        'img': img})
