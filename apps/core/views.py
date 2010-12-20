# coding: utf-8
from apps.news.forms import  ApproveActionForm
from apps.core import get_skin_template,benchmark
from apps.core.forms import SearchForm,SettingsForm,AddEditCssForm
from apps.core.models import Settings,Announcement,Css
from apps.core.decorators import benchmarking
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext,Template,Context
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from apps.news.models import News
#OBSOLETE
#from apps.helpers.diggpaginator import DiggPaginator as Paginator

from django.core.paginator import InvalidPage, EmptyPage
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template
from apps.core.helpers import get_settings,paginate,get_object_or_none,can_act
from django.shortcuts import get_object_or_404
#simple

def action_approve_simple(request,url,message):
    if not url:
        return HttpResponseRedirect('/')

    template = get_skin_template(request.user, 'approve_action.html')
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            return render_to_response(template,
                {'form': form,
                'url': url,
                'message': message},
                context_instance=RequestContext(request))
    else:
        form = ApproveActionForm()
        form.fields['url'].initial = url
        return render_to_response(template,
            {'form': form,
            'url': url,
            'message': message},
            context_instance=RequestContext(request))

#advance
@login_required
@can_act
def approve_action(request,obj_id=None, url='', \
    message='Do you want to "execute" this action?', action_function='',
        action_type=None,pk='id',ident=''):
    if obj_id is None:
        return HttpResponseRedirect('/')
    if url:
        #action will be executed via redirect to action function defined
        #by user
        url = url.replace('\%s', str(obj_id))
    else:
        url = '.' #action will be executed via this function with help of
        # action_function
    template = get_skin_template(request.user, 'approve_action.html')
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            if action_function:
                #function = globals()[action_function]
                action_module = action_function[:action_function.rindex('.')]
                action_function = action_function[action_function.rindex('.')+1:]
                action_module_instance = __import__(action_module,{},{},[''],level=0)
                action_function_instance = getattr(action_module_instance,action_function)
                #print "action_module: %r\naction_function_instance: %r" % (action_module,action_function_instance)
                #pk - primary key for following object 
                kwargs = {
                        'request': request,
                        pk:obj_id,
                    }

                if not action_type:
                    return action_function_instance(**kwargs)
                kwargs['action'] = action_type
                return action_function_instance(**kwargs)
        else:
            return render_to_response(template,
                {'form': form,
                'message': message,
                'url': url,
                },
                context_instance=RequestContext(request))
    else:
        form = ApproveActionForm()
        try:
            form.fields['url'].initial = request.META['HTTP_REFERER']
        except KeyError:
            form.fields['url'].initial = '/'
        return render_to_response(template,
            {'form': form,
            'message': message,
            'url': url},
            context_instance=RequestContext(request))

@benchmarking
def search(request):
    template = get_skin_template(request.user,'search.html')
    session = request.session
    query = request.POST.get('query','')
    #if query:
    #    session['search_q'] = query

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
    else:
        if request.get_full_path() == reverse('apps.core.views.search'):
            if 'search_q' in session:
                del session['search_q']
    query = query or session.get('search_q','')
    if query == '':
        form = SearchForm()
        return render_to_response(template,
            {'form': form},
            context_instance=RequestContext(request))
    #search algorithm IS 'ere!
    #print dir(settings)
    search_map=settings.CORE_SEARCH_MAP
    qset = Q(content__icontains=query)
    objects = list()
    for i in settings.CORE_SEARCH_FIELDS:
        app,model,search_values,options = i
        ct_object = ContentType.objects.get(app_label=app,model=model)
        kw = {}
        if search_values:
            search_map = search_values
        else:
            search_map = settings.CORE_SEARCH_MAP
        for m in search_map:
            if m in ct_object.model_class().__doc__:
                kw['%s__icontains'%m] = query
                qset = qset|(Q(**kw))
                kw = {}
        objs = ct_object.model_class().objects.filter(qset,**options)
        """
        #marking objs
        for o in objs:
            for m in search_map:
                print m
                if m in o.__doc__:
                    value = getattr(o,m)
                    #make regular expression be here!
                    try:
                        value = value.replace(query,'<span style="color: red;">%s</span>' % query)
                        setattr(o,m,value)
                    except:
                        pass
        """
        
        page_number = request.GET.get('page',1)
        _pages_ = get_settings(request.user,'objects_on_page',30)
        objs = paginate(objs,page_number,pages=_pages_,
            model=ct_object.model_class()._meta.verbose_name_plural.title(),
            view='apps.core.views.search_model',
            raw_model=model)
        #deprecated
        #paginator = Paginator(objs,30)
        #try:
        #    paginator = paginator.page(page_number)
        #    paginator.number = page_number
        #    paginator.view = 'apps.core.views.search_model'
        #    paginator.model = ct_object.model_class()._meta.verbose_name_plural.title()
        #    paginator.raw_model = model
        #except (InvalidPage,EmptyPage):
        #    paginator = paginator.page(1)
        #    paginator.number = page_number
        #    paginator.view = 'apps.core.views.search_model'
        #    paginator.model = ct_object.model_class()._meta.verbose_name_plural.title()
        #    paginator.raw_model = model
        if objs.object_list:
            #objects.append(paginator)
            objects.append(objs)
        qset = Q()
    
    request.session['search_q'] = query

    return render_to_response(template,
        {'form':form,
        'query':query,
        'objects':objects,
        },context_instance=RequestContext(request,processors=[benchmark]))

@benchmarking 
def search_model(request,model):
    template = get_skin_template(request.user, 'search_model.html')
    from django.template.loader import get_template,TemplateDoesNotExist
    try:
        template_src = get_skin_template(request.user,'includes/search_%s.html' % model )
        template_t = get_template(template_src)
        template = template_src
    except TemplateDoesNotExist:
        pass
    form = SearchForm()
    try:
        ct = ContentType.objects.get(model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect('/search/failed')
    session = request.session
    query = session.get('search_q','')
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid(): query = form.cleaned_data['query']
    if query == '':
        form = SearchForm()
        return render_to_response(template,
            {'form':form},
            context_instance=RequestContext(request))

    search_fields = settings.CORE_SEARCH_FIELDS
    if not model in [f[1] for f in search_fields]:
        return HttpResponseRedirect('/search/failed')
    model_idx = [f[1] for f in search_fields].index(model)
    search_keywords = [f[2] for f in search_fields][model_idx]
     
    #print "query:%s " % query
    if not search_keywords: search_keywords = settings.CORE_SEARCH_MAP
    qset = Q()
    for skwd in search_keywords:
        kw = {}
        if skwd in ct.model_class().__doc__:
            kw['%s__icontains' % skwd] = query
            qset = qset|Q(**kw)
    objects = ct.model_class().objects.filter(qset)
    _pages_ = get_settings(request.user,'objects_on_page',30)
    page_number = request.GET.get('page',1)
    objects = paginate(objects,page_number,pages=_pages_)

    form.fields['query'].initial = query or ''
    request.session['search_q'] = query or ''
    return render_to_response(template,
        {'objects':objects,
        'form': form,
        'query': query},
        context_instance=RequestContext(request,processors=[benchmark]))

    #return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
#IT BLOWS MY MIND ;) sometimes and i can not believe that i've written this block of code
def user_settings(request):
    template = get_skin_template(request.user,'settings.html')
    try:
        user_settings = Settings.objects.get(user=request.user)
    except Settings.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    _values_ = user_settings.get_decoded()
    form = SettingsForm()
    for k in _values_.keys():
        if k in form.fields:
            form.fields[k].initial = _values_[k]
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            from apps.core.settings import SETTINGS as FIELD_SETTINGS
            data_store = {}
            for k in FIELD_SETTINGS.keys():
                data_store[k] = cleaned_data.get(k,FIELD_SETTINGS[k])
            _buffer_ = user_settings.get_decoded()
            _buffer_.update(data_store)
            user_settings.store_data(_buffer_)
            user_settings.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
        else:
            return direct_to_template(request,template,{'form': form})
    else:
        
        return direct_to_template(request,template,{'form':form})

#sets settings only permitted
@login_required
def set_settings(request,key,value):
    from apps.core.settings import SECURE_SETTINGS
    if key in SECURE_SETTINGS:
        u_settings = Settings.objects.get(user=request.user)
        u_settings.store_data({key:value})
        u_settings.save()
        template = Template("[success]")
        context = Context()
        html = template.render(context)
        return HttpResponse(html)
    else:
        error_msg = u'Permission denied'
        return HttpResponseServerError(error_msg)

@login_required
def view_subscription(request):
    template = get_skin_template(request.user,'subscription.html')
    subscription = Announcement.objects.filter(Q(users=request.user)|Q(notified_users=request.user)).distinct()
    _pages_ = get_settings(request.user,'objects_on_page',20)
    #paginator = Paginator(subscription,_pages_)
    #try:
    #    page = request.GET.get('page',1)
    #    subscription = paginator.page(page)
    #    subscription.number = int(page)
    #except (EmptyPage,InvalidPage):
    #    subscription = paginator.page(1)
    #    subscription.number = 1
    subscription = paginate(subscription,request.GET.get('page',1),pages=_pages_)

    return direct_to_template(request,template,{'subscription':subscription})

@login_required
def delete_subscription(request,id,action=''):
    """ deletes the subscription"""
    user = request.user
    try:
        announcement = Announcement.objects.get(id__exact=id)
    except Announcement.DoesNotExist:
        return HttpResponseRedirect('/announcement/does/not/exist')
    announcement.users.remove(user)
    announcement.notified_users.remove(user)
    announcement.save()

    referer = request.META.get('HTTP_REFERER','/')
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            referer = form.cleaned_data['url']
    return HttpResponseRedirect(referer)

def show_comments(request,model,object_pk):
    from django.contrib.comments.models import Comment
    from django.contrib.contenttypes.models import ContentType
    template = get_skin_template(request.user,'base_comments.html')
    ct = get_object_or_404(ContentType,model=model)
    comments = Comment.objects.filter(content_type=ct,object_pk=str(object_pk))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    #paginator = Paginator(comments,_pages_)
    page = request.GET.get('page',1)
    #try:
    #    comments = paginator.page(page)
    ##    comments.number = int(page)
    #except (InvalidPage,EmptyPage):
    #    comments = paginator.page(1)
    #    comments.number = 1
    comments = paginate(comments,page,pages=_pages_) 
    return direct_to_template(request,template,{'comments':comments,'page':comments})

@login_required
def db_css(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/css'
    css = get_object_or_none(Css,user=request.user)
    if css:
        response.write(css.css)
    else:
        response.write('/**/')
    return response

@login_required
def add_edit_css(request):
    template = get_skin_template(request.user,'css_edit.html') 
    css = get_object_or_none(Css,user=request.user)
    form = AddEditCssForm()
    if request.method == 'POST':
        form = AddEditCssForm(request.POST,request=request)
        if form.is_valid():
            if css:
                css.css = form.cleaned_data['css']
            else:
                css = Css(user=request.user,css=form.cleaned_data['css'])
            css.save()
            return direct_to_template(request,template,{'form': form})
        else:
            return direct_to_template(request,template,{'form':form})
    else:
        if css:
            form.fields['css'].initial = css.css
        return direct_to_template(request,template,{'form':form})
