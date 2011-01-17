# Create your views here.
# ^^, coding: utf-8 ^^,
#from settings import MEDIA_ROOT,FROM_EMAIL
from apps.vote.models import Vote,Rate
from apps.vote.forms import VoteForm
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse,HttpResponseServerError
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
#from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
#from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, InvalidPage
#from django.core import serializers
from django.db.models.loading import get_model
#from django.contrib.auth.models import User
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
#from django.core.mail import send_mail
#from django.forms.util import ErrorList
#from apps.wh.forms import UploadAvatarForm,UpdateProfileForm,PMForm, RegisterForm, AddWishForm,PasswordChangeForm, PasswordRecoverForm
#from apps.core import make_links_from_pages as make_links
from apps.core import get_skin_template
from apps.core.helpers import get_settings,paginate,get_content_type_or_none,\
    get_object_or_none
#from cStringIO import StringIO
#import Image
#from datetime import datetime,timedelta
#from hashlib import sha1
#from random import randint, random
from django.template import Template,Context
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from apps.core.decorators import has_permission
from apps.vote.decorators import vote_allow_objects
from apps.core.helpers import can_act
#filters
#from apps.news.templatetags.newsfilters import spadvfilter
#from django.template.defaultfilters import striptags
#import os

@login_required
@vote_allow_objects(settings.ALLOW_VOTE_OBJECTS)
@can_act
def vote_rate(request,app_label='',model_name='',obj_id=0,rate=0):
    cleanse_null_votes()
    referer = request.META.get('HTTP_REFERER','/')
    if not rate:
        return HttpResponseRedirect(referer)
    if app_label:
        ct = ContentType.objects.get(model=model_name,app_label=app_label)
    else:
        ct = ContentType.objects.get(model=model_name)
    try:
        vote = Vote.objects.get(content_type=ct,object_pk=str(obj_id))
        #check if user voted
        try:
            user = vote.users.get(id=request.user.id)
        except User.DoesNotExist:
            vote.score += int(rate)
            vote.votes += 1
            vote.users.add(request.user)
            rate = Rate(content_type=ct, object_pk=obj_id, rate=int(rate),user=request.user)
            rate.save()
            vote.rates.add(rate)
            vote.save()
    except Vote.DoesNotExist:
        vote = Vote(content_type=ct,object_pk=str(obj_id))
        #check if object exist
        model = get_model(app_label=ct.app_label,model_name=ct.model)
        try:
            object = model.objects.get(pk=str(obj_id))
            vote.score = int(rate)
            vote.votes = 1
            vote.save() #presaving before adding users
            vote.users.add(request.user)
            #single rate
            rate = Rate(rate=int(rate),user=request.user,content_type=ct,object_pk=obj_id)
            rate.save()
            vote.rates.add(rate)
            vote.save()
        except: #object does not exist
            pass
    return HttpResponseRedirect(referer)

#Ehm, it feeds :) the memory, the proc resources
#We should something to do
def cleanse_null_votes():
    #make cleanse votes that link on deleted objects from db
    votes = Vote.objects.all()
    for vote in votes:
        object_model = get_model(app_label=vote.content_type.app_label,
            model_name=vote.content_type.model)
        try:
            object_id = object_model.objects.get(pk=str(vote.object_pk))
        except: #does not exist
            vote.delete()
    return

#Admin's only or public?
def show_voted(request, id):
    template = get_skin_template(request.user,'user_voted.html')
    try:
        vote = Vote.objects.get(id=id)
    except Vote.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    rates = vote.rates.distinct()
    _pages_ = get_settings(request.user,'rates_on_page',200)
    page = request.GET.get('page',1)
    rates = paginate(rates,page,pages=_pages_)
    return direct_to_template(request,template,{'vote': vote,'rates':rates})
    
    #return render_to_response(template,
    #    {'vote':vote},
    #    context_instance=RequestContext(request) )

#@has_permission('auth.can_test')
def show_best(request,app_model):
    template = get_skin_template(request.user,'votes_best.html')
    try:
        ct = ContentType.objects.get(model=app_model)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    #objects = ct.
    #implement new ObjectManager
    votes = Vote.best_objects.filter(content_type=ct).order_by('-votes')[:10]
    _pages_ = get_settings(request.user,'rates_on_page',40)
    page = request.GET.get('page',1)
    votes = paginate(votes,page,pages=_pages_)
    return direct_to_template(request,template,{'votes':votes})

@login_required
@can_act
def comment_rate(request,id):
    template = get_skin_template(request.user,'comment_rate.html')
    rate = get_object_or_none(Rate,id=id)
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            if rate:
                rate.comment = form.cleaned_data['comment']
            else:
                return HttpResponseRedirect('/vote/rate/does/not/exist')
            rate.save()
            return HttpResponseRedirect(form.cleaned_data.get('next','/'))
        else:
            print form.errors
            return direct_to_template(request,template,{'form':form})
    else:
        form = VoteForm()
        form.fields['next'].initial = request.META.get('HTTP_REFERER','/')
        if rate:
            form.fields['comment'].initial = rate.comment
        return direct_to_template(request,template,{'form':form})
