# Create your views here.
# ^^, coding: utf-8 ^^,
import os
from apps.news.models import News,Category,ArchivedNews
from apps.news.forms import ArticleForm
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
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core import serializers
from datetime import datetime,timedelta
from os import stat
#filters
from apps.news.templatetags.newsfilters import spadvfilter,bbfilter, render_filter
from django.template.defaultfilters import striptags
from apps.tracker.decorators import user_visit
from apps.core.helpers import get_settings,save_comment,paginate,can_act
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

@login_required
#@has_permission('comments.change_comment') #blocks the comment edition
def edit_comment(request, id=0):
    template = get_skin_template(request.user, "edit_comment_ng.html")
    can_edit_comments = request.user.has_perm('news.edit_comments') 
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return HttpResponseRedirect('/comment/not/found')
    if request.user != comment.user and not can_edit_comments\
    and not request.user.is_superuser:
        return HttpResponseRedirect('/comment/not/found')
    if request.method == 'POST':
        form = CommentForm(request.POST,request=request)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            url = form.cleaned_data['url']
            _jump = request.GET.get('j',None) 
            if _jump: url += "#j=%s" % _jump
            syntax = form.cleaned_data['syntax']
            c = Comment.objects.get(id=id)
            c.comment = comment
            c.syntax = syntax
            c.save()
            if url:
                return HttpResponseRedirect(url)
            return HttpResponseRedirect('/comment/edit/successfull') #request.META['HTTP_REFERER']
        else:
            return render_to_response(template,
                {'form':form},
                context_instance=RequestContext(request))
    form = CommentForm()
    form.fields['comment'].initial = comment.comment;
    if request.META.get('HTTP_REFERER',None):
        referer = "%s%s" % (request.META['HTTP_REFERER'], "#c%i" % int(id) )
    else: referer = '/'
    form.fields['url'].initial = referer
    form.fields['syntax'].initial = comment.syntax
    return render_to_response(template,
        {'form':form},
        context_instance=RequestContext(request))

#TODO: MAKE IT MORE SAFETY!!!
def get_comment(request, id=0,raw=False):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        #FIXME: Fix this dirty hack :) //fixed via js
        #from time import sleep
        #sleep(0.125)
        comment = Comment.objects.get(id__exact=id)
        if not raw:
            comment.comment = striptags(comment.comment)
            comment.comment = render_filter(comment.comment, comment.syntax) #striptags|spadvfilter|safe
        response.write(serializers.serialize("json",[comment]))
        return response
    except Comment.DoesNotExist:
        response.write(serializers.serialize("json",[]))
        return response

@login_required
def edit_comment_ajax(request, id=0):
    template = get_skin_template(request.user, 'edit_comment.html')
    can_edit_comments = request.user.has_perm('news.edit_comments') 
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        error_msg = u"Comment not found"
        return HttpResponseServerError(error_msg)
    if request.user != comment.user and not can_edit_comments\
    and not request.user.is_superuser:
        error_msg = u"Permission Denied"
        return HttpResponseServerError(error_msg)
    if request.method == 'POST':
        post = request.POST.copy()
        if post.has_key('comment'):
            if comment.comment != post['comment']: #prevent db from rewrite data which did changed 
                comment.comment = post['comment']
                #comment.submit_date=datetime.now()
                #DDoS prevention
                if hasattr(request.user,'useractivity') and not request.user.is_superuser and not request.user.is_staff:
                    if request.user.useractivity.last_action_time is not None:
                        if request.user.useractivity.last_action_time > datetime.now()-timedelta(seconds=15):
                            error_msg = u"timeout"
                            return HttpResponseServerError(error_msg)
                request.user.useractivity.last_action_time = datetime.now()
                request.user.useractivity.save()
                comment.save()
            #return HttpResponseRedirect(comment.get_absolute_url())
            template = Template("[success]")
            context = Context()
            html = template.render(context)
            return HttpResponse(html)
        else:
            error_msg = u"Unknow data is submitted"
            return HttpResponseServerError(error_msg)
    else:
        error_msg = u"no POST data was sent"
        return HttpResponseServerError(error_msg)


@login_required
#@has_permission('news.del_restore_comments')
def del_restore_comment(request,id=0,flag='delete'):
    can_del_restore_comments =  request.user.has_perm('news.del_restore_comments') #if smb can edit news
    can_purge_comments =  request.user.has_perm('news.purge_comments') #if smb can edit news
    try:
        referer = request.META['HTTP_REFERER']
        jump = request.GET.get('j',None)
        if jump: referer += "#c%s" % jump
    except KeyError:
        referer = None
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return HttpResponseRedirect('/comment/not/found')

    if request.user != comment.user\
    and not can_del_restore_comments\
    and not request.user.is_superuser:
        return HttpResponseRedirect('/comment/not/found')
    if flag in 'delete':
        comment.is_removed = True
        comment.save()
        if referer:
            return HttpResponseRedirect(referer)
        return HttpResponseRedirect('/comment/deleted')
    if flag in 'restore':
        comment.is_removed = False
        comment.save()
        if referer:
            return HttpResponseRedirect(referer)
        return HttpResponseRedirect('/comment/restored')
    return HttpResponseRedirect('/')

@login_required
def purge_comment_old(request,id=0):
    #only superuser and can_purge_comments can delete comments
    can_purge_comments =  request.user.user_permissions.filter(codename='purge_comments') #if smb can edit news
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return HttpResponseRedirect('/comment/not/found')
    if request.user.is_superuser or can_purge_comments:
            message = _('Do you realy want to PURGE this comment?')
            return action_approve_simple(request,'/comment/%s/purge' % comment.id, message)
    return HttpResponseRedirect('/')

@login_required
def purge_comment(request,id=0,approve='force'):
    next = ''
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            next = form.cleaned_data['url'] #from where we get here ;)
    can_purge_comments = request.user.user_permissions.filter(codename='purge_comments')
    try:
        comment = Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return HttpResponseRedirect('/comment/not/found')
    if request.user.is_superuser or can_purge_comments:
        comment.delete()
        if next:
            return HttpResponseRedirect(next)
        return HttpResponseRedirect('/comment/purged')
    else:
        return HttpResponseRedirect('/comment/not/found')

def sphinx_news(request):
    template = get_skin_template(request.user, 'sphinx_news.html')
    if request.method == 'POST':
        form = SphinxSearchForm(request.POST)
        if form.is_valid():
            news = News.search.query(form.cleaned_data['query']).all()
            return direct_to_template(request, template,
                {'form': form, 'news': news})
        else:
            return direct_to_template(request, template,
                {'form': form})
    form = SphinxSearchForm()
    return direct_to_template(request, template,
        {'form': form})
