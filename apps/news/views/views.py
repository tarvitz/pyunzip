# Create your views here.
# ^^, coding: utf-8 ^^,
import os
from apps.news.models import News,Category,ArchivedNews, Meating
from apps.news.forms import ArticleForm, ArticleModelForm, AddMeatingForm
from apps.core.forms import CommentForm, SphinxSearchForm
from apps.files.models import Attachment
from apps.files.helpers import save_uploaded_file as save_file
from apps.core import make_links_from_pages as make_links
from apps.core import pages, get_skin_template
from apps.core.views import action_approve_simple
#deprecated
#from django.views.generic.simple import direct_to_template
#overriding
from apps.core.shortcuts import direct_to_template
from apps.core.forms import ApproveActionForm
#from apps.settings import MEDIA_ROOT
from django.conf import settings
from django.template import RequestContext,Template,Context
from django.contrib import auth
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User,Permission
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import InvalidPage, EmptyPage
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core import serializers
from django.core.urlresolvers import reverse
from datetime import datetime,timedelta
from os import stat
#filters
from apps.news.templatetags.newsfilters import spadvfilter,bbfilter, render_filter
from django.template.defaultfilters import striptags
from apps.tracker.decorators import user_visit
from apps.core.helpers import get_settings,save_comment,paginate,can_act, handle_uploaded_file
from apps.core.decorators import benchmarking,update_subscription_new,has_permission,render_to
from apps.core import benchmark #processors

#def get_a_normal_browser(request):
#    agent = request.META['HTTP_USER_AGENT']
#    if 'msie 6.0' in agent.title().lower()\
#    or 'msie 7.0' in agent.title().lower():
#        return HttpResponseRedirect('you/should/fuifuill/your/destiny')

@benchmarking
def archived_news(request,year='',month='',day=''):
    template = get_skin_template(request.user, 'archived_news.html')
    news = ArchivedNews.objects.all().order_by('-date')
    _pages_ = get_settings(request.user,'news_on_page',10)
    page = request.GET.get('page',1)
    news = paginate(news,page,pages=_pages_)

    return render_to_response(template,{'news':news,'page':news},
        context_instance=RequestContext(request,processors=[benchmark]))
    #return direct_to_template(request,template,{'news':news,'page':news})

#@render_to('news/archived_article.html')
def show_archived_article(request,id):
    ct = ContentType.objects.get(app_label='news',model='archivednews')
    comments = Comment.objects.filter(content_type=ct,object_pk=str(id))
    template = get_skin_template(request.user,'news/archived_article.html')
    try:
        article = ArchivedNews.objects.get(id=id)
    except ArchivedNews.DoesNotExist:
        return HttpResponseRedirect('/article/does/not/exist')
    _pages_ = get_settings(request.user,'news_on_page',30)
    page = request.GET.get('page',1)
    comments = paginate(comments,page,pages=_pages_,jump='#comments')
    #returns via render_to decorator
    return direct_to_template(request,template,{'article':article,'comments':comments})
#test it

#@permission_required('files.purge_replay') #works
#@has_permission('can_test_t') #works
@benchmarking
def news(request,approved='approved',category=''):
    template = get_skin_template(request.user,'news.html')
    can_approve_news = None
    if request.user.is_authenticated():
        can_approve_news = request.user.user_permissions.filter(codename='edit_news')

    page = request.GET.get('page',1)

    #make an archives
    now = datetime.now()
    td = timedelta(days=365)
    older = now - td
    all_news = News.objects.all()
    for n in all_news:
        if  older > n.date:
            n.archive()
    #TODO: DELETE duplicated code
    if request.user.is_superuser or can_approve_news:
        news = News.objects.all().order_by('-date').filter(category__name__icontains=category)
        if  approved == 'unapproved':
            news = News.objects.filter(approved__exact=False).order_by('-date')
            _pages_ = get_settings(request.user,'news_on_page',30)
            news = paginate(news,page,pages=_pages_)
            return render_to_response(template,{'news':news,'page':news},
                context_instance=RequestContext(request,processors=[benchmark]))

    else:
        news = News.objects.filter(approved__exact=True).order_by('-date')
    _pages_ = get_settings(request.user,'news_on_page',30)
    news = paginate(news,page,pages=_pages_,
        view='apps.news.views.news')
    return render_to_response(template,
        {'news': news,
        'page': news},
        context_instance=RequestContext(request,
            processors=[benchmark]))


def search_article(request):
    template = get_skin_template(request.user, "news/search.html")
    return render_to_response(template, {'form':''},
    context_instance=RequestContext(request))

@update_subscription_new(app_model='news.news',pk_field='number')
@user_visit(object_pk='number',ct='news.news')
def show_article(request, number=1,object_model='news.news'):
    template = get_skin_template(request.user,'news/article.html')
    page = request.GET.get('page',1)
    can_edit_news = None
    if hasattr(request.user, 'skin'):
        can_edit_news = request.user.has_perm('news.edit_news')
    #Let staff users allow to get the access for the articles,
    #may be dangerous
    try:
        if request.user.is_superuser or can_edit_news:
            article = News.objects.get(id__exact=number)
        else:
            article = News.objects.get(id__exact=number,approved=True)
            #merging head_content and content with each other
    except News.DoesNotExist:
            return HttpResponseRedirect('/article/doesnot/exist')
    news_type = ContentType.objects.get(app_label='news', model='news')
    comments = Comment.objects.filter(content_type=news_type.id, object_pk=str(article.id))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    comments = paginate(comments,page,pages=_pages_)
    """
    #checks for validation and saves a comment
    if hasattr(request.user,'nickname'):
        redirect = save_comment(request=request,template=template,
            vars={'article':article,
            'comments':comments,'page':comments},ct=news_type,object_pk=article.id,
            redirect_to=request.META.get('HTTP_REFERER','/'))
        if 'success' in redirect:
            if redirect['success']:
                return HttpResponseRedirect(redirect['redirect'])
            else:
                return direct_to_template(request,template,
                    {'article':article,
                    'page':comments,
                    'form':redirect['form']})
    """
    #app_n_model breaks functionallity
    #form = CommentForm(app_n_model='news.news',obj_id=number,request=request)
    form = CommentForm(request=request,initial={'app_n_model':'news.news','obj_id': number,'url':
        request.META.get('PATH_INFO',''),'page':request.GET.get('page','')})
    return render_to_response(template,
        {'article': article,
        'comments': comments,
        'form': form,
        'page': comments},
        context_instance=RequestContext(request,
            processors=[pages]))

#@semiobsolete, better use action_article
@login_required
def article_action(request,id=None,action=None):
    if not action or not id:
        return HttpResponseRedirect('/')
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError:
        referer = None
    can_approve = request.user.user_permissions.filter(codename='edit_news')
    next = ''
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            next = form.cleaned_data['url']
    try:
        article = News.objects.get(id=id)
    except News.DoesNotExist:
        return HttpResponseRedirect('/article/doesnot/exist')
    if request.user.is_superuser or can_approve:
        if action == 'approve':
            article.approved = True
        if action == 'unapprove':
            article.approved = False
        if action == 'delete':
            article.delete()
        if action != 'delete':
            article.save()
        #return HttpResponseRedirect(article.get_absolute_url()) //too simple to uz
        #we should use more clear way to interact with articles and retrieve
        #urls via last url state ;)
        if next:
            return HttpResponseRedirect(next)
        if referer:
            return HttpResponseRedirect(referer)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/permission/denied')

#@obsolete
@login_required
@can_act
def add_article(request,id=None,edit_flag=False):
    can_edit =  request.user.has_perm('news.edit_news') #if smb can edit news
    template = get_skin_template(request.user,'news/add.html')
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            if request.user.is_staff: approved = True
            else: approved = False
            url = form.cleaned_data['url']
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            editor = form.cleaned_data['editor']
            head_content = form.cleaned_data['head_content']
            syntax = form.cleaned_data['syntax']
            if head_content is None: head_content = ''
            content = form.cleaned_data['content']
            #is it dangerous?
            category = form.cleaned_data['category']
            #attachment block
            attachment_data = form.cleaned_data['attachment']
            c = Category.objects.get(id=category)
            date = datetime.now()
            author_ip = request.META['REMOTE_ADDR']
            if not edit_flag: #adding new article
                article = News(url=url,title=title,author=author,editor=editor,head_content=head_content,
                    content=content,category=c,date=date,
                    author_ip=author_ip, approved=approved,syntax=syntax)
            else: #editing old article
                if not can_edit and not request.user.is_staff and not request.user.is_superuser:
                    return HttpResponseRedirect('/')
                article = News.objects.get(id=id)
                article.title = title
                article.author = author
                article.url = url
                article.editor = editor
                article.head_content = head_content
                article.content = content
                article.category = c
                #article.date = date
                article.author_ip = author_ip
                article.approved = True
                article.syntax = syntax

            if attachment_data:
                if len(attachment_data.name)>30:
                    return HttpResponseRedirect('/attchment/name/is/too/long')
                path = save_file(attachment_data, os.path.join(settings.MEDIA_ROOT, "attachments"))
                if not path:
                    return HttpResponseRedirect('/attachment/already/exists')
                atm = Attachment(attachment=path) #saving the attachment
                atm.save()
                article.attachment = atm
            #set locks to prevent agression spam attacks ;)
            user = request.user
            if hasattr(user,'useractivity'):
                if user.useractivity.last_action_time is not None:
                    if not user.is_superuser:
                        if user.useractivity.last_action_time > datetime.now()-timedelta(minutes=2):
                            return HttpResponseRedirect('/article/add/timeout')
            article.save()
            user.useractivity.last_action_time = datetime.now()
            user.useractivity.save()
	    if approved:
	    	return HttpResponseRedirect(article.get_absolute_url())
            else:
                return HttpResponseRedirect('/article/created/')
            #return HttpResponseRedirect('/article/%s' % str(article.id))

        else:
            return render_to_response(template,
                {'form': form,
                'edit_flag': edit_flag},
                context_instance=RequestContext(request))
    else:
        #print request.user.is_staff
        form = ArticleForm()
        if edit_flag:
            if not can_edit and not request.user.is_staff and not request.user.is_superuser:
                return HttpResponseRedirect('/')
            try:
                article = News.objects.get(id=id)
            except News.DoesNotExist:
                return HttpResponseRedirect('/article/not/found')
            map = ['title','url','editor','head_content','content','author','syntax']
            for i in map:
                form.fields[i].initial = getattr(article,i)
            form.fields['category'].initial = article.category.id

        return render_to_response(template,
            {'form': form,
            'edit_flag': edit_flag},
            context_instance=RequestContext(request))

#make it
@login_required
@can_act
def action_article(request, id=None, action=None):
    template = get_skin_template(request.user, 'news/action_article.html')
    article_instance = None
    if action: #None means add article, other actions depends on instance existance
        article_instance = get_object_or_404(News, id=id)
    if request.method == 'POST':
        form = ArticleModelForm(request.POST, instance=article_instance)
        if form.is_valid():
            if not action:
                form.instance.author_ip = request.META.get('REMOTE_ADDR','127.0.0.1')
                form.instance.date = datetime.now()
                form.instance.author = form.cleaned_data.get('author', None) or\
                    request.user.nickname
                if request.user.has_perm('news.add_news') or request.user.is_superuser:
                    form.instance.approved = True
                form.save()
                return HttpResponseRedirect(reverse('news:article',
                    args=(form.instance.id, ))
                )
            elif action == 'edit':
                form.instance.editor = request.user.nickname
                form.save()
                next = form.cleaned_data.get('next', None) or \
                    reverse('news:article', args=(form.instance.id, ))
                return HttpResponseRedirect(next)
        else:
            return direct_to_template(request, template,
                {'form': form})
    form = ArticleModelForm(instance=article_instance,
        initial={'next': request.META.get('HTTP_REFERER', None)})
    return direct_to_template(request, template, {'form': form})

def sphinx_search_news(request):
    template = get_skin_template(request.user, 'includes/sphinx_search_news.html')
    if request.method == 'POST':
        form = SphinxSearchForm(request.POST)
        if form.is_valid():
            news = News.search.query(form.cleaned_data['query']).all()
            page = request.GET.get('page',1)
            _pages_ = get_settings(request.user, 'news_on_page', 20)
            news = paginate(news, page, pages=_pages_)
            return direct_to_template(request, template,
                {'form': form, 'news': news, 'query': form.cleaned_data['query']})
        else:
            return direct_to_template(request, template,
                {'form': form, 'query': form.cleaned_data['query']})
    form = SphinxSearchForm()
    return direct_to_template(request, template,
        {'form': form})

def view_meatings(request):
    template = 'meatings.html'
    meatings = Meating.objects.all()
    meatings = paginate(meatings, request.GET.get('page', 1), pages=20)
    return direct_to_template(request, template, {'meatings': meatings})

def view_meating(request, id):
    template = 'meating.html'
    meating = get_object_or_None(Meating, id=id)
    return direct_to_template(request, template, {'meating': meating})

@has_permission('news.add_meating')
def add_meating(request):
    template = 'add_meating.html'
    form = AddMeatingForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('news:index'))
    return direct_to_template(request, template, {'form': form})
