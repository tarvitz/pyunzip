# coding: utf-8
import os
from apps.news.forms import  ApproveActionForm
from apps.core import get_skin_template,benchmark
from apps.core.forms import SearchForm,SettingsForm,AddEditCssForm,CommentForm,RequestForm
from apps.core.models import Settings,Announcement,Css
from apps.core.decorators import benchmarking,progress_upload_handler
from apps.core.helpers import validate_object

from django.utils.translation import ugettext_lazy as _, ugettext as _t
from django.template import RequestContext,Template,Context
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from apps.news.models import News
#OBSOLETE
#from apps.helpers.diggpaginator import DiggPaginator as Paginator

from django.core.paginator import InvalidPage, EmptyPage
from django.contrib.contenttypes.models import ContentType
from apps.core.shortcuts import direct_to_template
from apps.core.helpers import get_settings,paginate,get_object_or_none,can_act,get_content_type,\
    handle_uploaded_file,get_upload_form,get_upload_helper
from apps.core.handlers import UploadProgressHandler
from django.shortcuts import get_object_or_404
import simplejson
import logging
logger = logging.getLogger(__name__)

#simple

#additional modules
#from apps.tracker.decorators import user_add_content

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
@login_required
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

def get_ip_address(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/plain'
    from apps.helpers import get_self_ip_address
    ip = get_self_ip_address()
    response.write(ip or 'none detected')
    return response

from apps.tracker.decorators import new_comment
@new_comment
@login_required
def save_comment(request):
    #obj_id could cause a lot of problems if it would have much bigger blocks
    #of data then simple strings or numbers
    #use it careful until it's overwritten
    
    template = get_skin_template(request.user, 'add_comments_site.html')
    if request.method == 'POST':
        form = CommentForm(request.POST,request=request)
        if form.is_valid():
            app_n_model = form.cleaned_data['app_n_model']
            obj_id = form.cleaned_data['obj_id']
            #Prevent saving comment for void
            if not validate_object(app_n_model,obj_id):  #app_label.model 13 for example
                return HttpResponseRedirect('/comment/could/not/be/saved') #replace it with something wise 

            ct = get_content_type(app_n_model) #we had already checked up existance of single object
            comment = form.cleaned_data['comment']
            syntax = form.cleaned_data['syntax']
            hidden_syntax = form.cleaned_data['hidden_syntax']
            subscribe = form.cleaned_data['subscribe'] #implement announcement here
            unsubscribe = form.cleaned_data['unsubscribe'] #WTF??? Cleanse this as soon as possible
            #saving comment
            
            c = Comment.objects.filter(content_type=ct,object_pk=str(obj_id),
                user=request.user).order_by('-submit_date')
            #print "Comment: ",c
            #exists, updating
            from datetime import datetime
            now = datetime.now()
            if c: #exists
                c = c[0]
                if c.user == request.user and c.comment != comment: #is equal
                    #new comment and not a dublicate
                    c.comment += "\n"+comment
                    c.submit_date = now
                    ip = request.META.get('REMOTE_ADDR','')
                    if ip: c.ip_address = ip
                    c.save()
            if not c: #looks not great :)
                c = Comment(user=request.user,syntax=syntax,submit_date=now,
                    is_public=True,content_type=ct,object_pk=str(obj_id),site_id=1)
                c.comment = comment
                c.save()
            url = form.cleaned_data['url']
            page = 'last'
            #deprecated :)
            #page = request.GET.get('page','') or form.cleaned_data['page']
            if page: url += '?page=%s' % page
            return HttpResponseRedirect("%s#c%i" % (url,c.id))
        else:
            return direct_to_template(request,template,{'form':form})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

#TODO: TEST IT right
@login_required
def edit_comment(request,id):
    template = get_skin_template(request.user, 'edit_comment_ng.html')
    c = get_object_or_none(Comment,id=id)
    if not c:
        return HttpResponseRedirect('/comment/not/found')

    if request.method == 'POST':
        form = CommentForm(request.POST, request=request)
        if form.is_valid():
            fields = ('comment','syntax',
                'hidden_syntax')
            for f in fields:
                setattr(c,f,form.cleaned_data[f])
            url = form.cleaned_data['url']
            c.save()
            _jmp = request.GET.get('j','')
            if _jmp: url += '#c%s' % _jmp
            return HttpResponseRedirect(url)
            
        else:
            return direct_to_template(request,template,{'form':form})
    url = request.META.get('HTTP_REFERER','/')
    _jmp = request.GET.get('j','') #We jump :)
    if _jmp: url += '#c%i' % c.id

    form = CommentForm(initial={'comment':c.comment,
        'syntax':c.syntax,'url':url
        })

    return direct_to_template(request,template,{'form':form,'comment_id':c.id})

@login_required
@progress_upload_handler
def upload_file(request,app_n_model,filefield): 
    logger.info('upload_file initialized')
    #print "initial"
    error = None
    progress_id = None
    #print request.GET
    #pId = request.GET.get('X-Progress-ID',None) 
    #print "pId: ", pId
    """It seems it's deprecated now """
    #if   'X-Progress-ID' in request.GET:
    #    prigress_id =  request.GET['X-Progress-ID']
    #elif 'X-Progress-ID' in request.META:
    #    progress_id = request.META['X-Progress-ID']
    #
    #print "Initializing upload UploadPogressHandler"
    progress_id = request.GET.get('X-Progress-ID',None)
    #request.upload_handlers.insert(0,UploadProgressHandler(request,progress_id)) #set via decorator
    #print "progress_id: ", progress_id
    if request.method == 'POST':
        #print "request POST initialized"
        #print "getting form via settings"
        if progress_id:
                cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
                status_data = request.session.get(cache_key,None)

        UploadForm = get_upload_form(app_n_model)
        helper_saver = get_upload_helper(app_n_model)
        if UploadForm is None or helper_saver is None:
            status_data = {'complete':True,'error':_t('invalid UploadForm has passed or improperly configurated')}
            request.session[cache_key] = status_data
            return HttpResponseServerError(_t('Invalid UploadForm has passed or improperly configurated'))
        #print "Form: ", UploadForm
        #it's kindda horror monkey patching method
        if not RequestForm in UploadForm.__bases__:
            UploadForm.__bases__ = (RequestForm,) + UploadForm.__bases__
        form = UploadForm(request.POST,request.FILES,request=request)
        #print "UploadForm initialized"
        #print form.is_valid()
        #getting some data before validation
        #print form.fields 
        if form.is_valid():
            #print "form is valid, saving file"
            #here we set where we saving
            from apps.core.settings import UPLOAD_SETTINGS
            save_to = os.path.join(UPLOAD_SETTINGS[app_n_model]['schema'],str(request.user.id))
            #Should we handle it?
            filename = handle_uploaded_file(request.FILES[filefield],save_to)
            #insert some sort of validation here
            error = None
            #error = validate_file(filename)
            if not error:
                #fd = open(filename,'rb')
                #saving file
                ct = get_content_type(app_n_model)
                #print "getting ct ", ct
                if ct:
                    #print "saving instance" 
                    pk = helper_saver(request,form)
                    instance = ct.model_class().objects.get(pk=pk)
                    setattr(instance,filefield,filename)
                    instance.save()
                #fd.close()
                return HttpResponse('Ok')
        else:
            #what shall we do it the form is invalid ? :D
            #print "form is invalid"
            #print form.errors
            #print "form.is_invalid()"
            if progress_id:
                #print "[1] progress id: ",progress_id
                cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
                #print request.session.keys()
                #it's very strange but it could not exists :)
                #i was shocked
                status_data = request.session.get(cache_key,None)
                #print "[a] ", status_data
                if status_data:
                    #print "[2] inserting errors: ", form.errors
                    status_data['error'] = form.errors
                    status_data.update({'errors': simplejson.dumps(form.errors)})
                    request.session[cache_key] = status_data
                    #print "[3] ",request.session[cache_key]
                else:
                    status_data = {'complete': True, 'error': form.errors.as_text(),
                        'errors': form.errors,
                    }
                    request.session[cache_key] = status_data
            response = HttpResponse()
            response['Content-Type'] = 'text/javascript'
            response.write(simplejson.dumps(form.errors.as_text()))
            return response
        if error:
            if status_data:
                status_data['error'] = error
                request.session[cache_key] = status_data
    return HttpResponse('NOT Ok') #<-wtf? 

def uploader_progress(request):
    """
    Return JSON object with information about the progress of an upload
    """
    #print "uploader_progress initialized"
    progress_id = request.GET.get('X-Progress-ID',None)
    #if   'X-Progress-ID' in request.GET:
    #    progress_id =  request.GET['X-Progress-ID']
    #elif 'X-Progress-ID' in request.META:
    #   progress_id = request.META['X-Progress-ID']
    #print "upload_progress progress_id: ",progress_id
    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        #print "getting data"
        data = request.session.get(cache_key, None)
        #print "data: ", data
        if data:
            if data['complete']:
                del request.session[cache_key]
                #print "response: ",simplejson.dumps(data)
            return HttpResponse(simplejson.dumps(data))
        else:
            return HttpResponseServerError(_t('Invalid X-Progress-ID have passed, or session key is missing'))
    else:
        #print "Server Error: You must provide X-Progress-ID header or query param."
        return HttpResponseServerError(_t('Server Error: You must provide X-Progress-ID header or query param.'))
