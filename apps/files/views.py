# Create your views here.

from django.shortcuts import render_to_response
from apps.core.shortcuts import direct_to_template
from django.template import RequestContext
from django.contrib import auth
from django.db.models import get_model,Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import InvalidPage, EmptyPage
from django.core.urlresolvers       import reverse
from django.core import serializers
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.http import HttpResponse,HttpResponseRedirect, Http404
from apps.files.forms import UploadReplayForm,\
    EditReplayForm, UploadImageForm, CreateGalleryForm, FileUploadForm, \
    UploadFileModelForm, UploadImageModelForm, UploadReplayModelForm,\
    ActionReplayModelForm, SimpleFilesActionForm, ImageModelForm
from apps.core.forms import CommentForm, action_formset, action_formset_ng
from apps.files.models import Replay, Gallery, Version, Game, File, Attachment
from apps.files.models import Image as GalleryImage
from apps.files.helpers import save_uploaded_file as save_file,save_thmb_image, is_zip_file
from apps.core.helpers import can_act, handle_uploaded_file
from apps.files.decorators import *
from apps.core.decorators import update_subscription,update_subscription_new,benchmarking, \
    check_user_fields
from apps.tracker.decorators import user_visit
from apps.core import make_links_from_pages as make_links
from apps.core import pages,benchmark, get_skin_template
from apps.core.forms import ApproveActionForm,SearchForm
#from settings import MEDIA_ROOT
from django.conf import settings
from datetime import datetime
from os import mkdir,stat
from cStringIO import StringIO
from apps.core.helpers import get_settings,save_comment,paginate
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
import zipfile
import bz2
import os


@login_required
@can_act
@csrf_protect
def upload_replay(request):
    template = get_skin_template(request.user, 'replays/upload_replay.html')
    if request.method == 'POST':
        form = UploadReplayModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.instance.upload_date = datetime.now()            
            form.save()
            return HttpResponseRedirect(reverse('files:replays'))
        else:
            return direct_to_template(request, template, {'form': form})
    form = UploadReplayModelForm()
    return direct_to_template(request, template, {'form': form})

@login_required
@can_act
@csrf_protect
@check_user_fields({'is_staff': True})
def upload_file(request):
    template = get_skin_template(request.user, 'files/upload_file.html')
    if request.method == 'POST':
        form = UploadFileModelForm(request.POST, request.FILES)
        if form.is_valid():
            file = handle_uploaded_file(request.FILES['file'],
                'files/%s' % request.user.id)
            form.instance.file = file
            form.instance.owner = request.user
            form.instance.upload_date = datetime.now()
            form.save()
            return HttpResponseRedirect(reverse('files:files'))
        else:
            return direct_to_template(request, template, {'form': form})
    form = UploadFileModelForm()
    return direct_to_template(request, template, {'form': form})

@login_required
@can_act
def upload_file_old(request):
    template = get_skin_template(request.user, 'files/upload_file_old.html')
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            raw_file_data = form.cleaned_data['file']
            description = form.cleaned_data['description']
            url = form.cleaned_data['url']
            owner = request.user
            if (raw_file_data.size/1024/1024)>10: #10mb file
                return HttpResponseRedirect('/upload/size/overlimited')
            file_path = save_file(raw_file_data,"%s/files/%s" % (settings.MEDIA_ROOT,request.user.id))
            if file_path == 0: #the same file was uploaded by the certain user
                return HttpResponseRedirect('/upload/already/finished/')
            if not file_path:
                return HttpResponseRedirect('/upload/failed')
            now = datetime.now()
            f = File(url=url,description=description,owner=owner,file=file_path,
                upload_date=now)
            f.save()
            return HttpResponseRedirect('/upload/successful')
        else:
            return render_to_response(template,
                {'form': form},
                context_instance=RequestContext(request))
    else:
        form = FileUploadForm()
        return render_to_response(template,
            {'form': form,},
            context_instance=RequestContext(request))

@login_required
def choose_game_to_upload(request):
    template = get_skin_template(request.user, 'replays/choose_game_to_upload.html')
    games = Game.objects.all()
    return render_to_response(template,
        {'games': games},
        context_instance=RequestContext(request))

@can_act
@csrf_protect
@login_required
def edit_replay(request, id):
    template = get_skin_template(request.user, 'replays/edit_replay.html')
    instance = get_object_or_404(Replay, id=id)
    if request.method == 'POST':
        form = ActionReplayModelForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('files:replay',
                args=(form.instance.pk, )))
        else:
            return direct_to_template(request, template,
                {'form': form})
        
    form = ActionReplayModelForm(instance=instance)
    return direct_to_template(request, template, {'form': form})

@login_required
@can_act
def edit_replay_old(request,id=0):
    template = get_skin_template(request.user, 'replays/upload_replay.html')
    can_edit = request.user.user_permissions.filter(codename='edit_replay')
    try:
        replay = Replay.objects.get(id=id)
        editable = (can_edit or request.user.is_superuser or request.user.is_staff or
            request.user == replay.owner)
        if not editable:
                return HttpResponseRedirect('/permission/denied')
    except Replay.DoesNotExist:
            return HttpResponseRedirect('/replay/does/not/exist') 
    map = ['name','type','nonstd_layout','teams','races','comments','version']
    if request.method == 'POST':
        form = EditReplayForm(request.POST, request.FILES)
        if form.is_valid():
            for key in map:
                setattr(replay,key,form.cleaned_data[key])
            replay.winner = int(form.cleaned_data['winners'])
	    replay.syntax = form.cleaned_data['hidden_syntax']
            replay.save()
            url = form.cleaned_data.get('url','/')
            return HttpResponseRedirect(url)
        else:
            del form.fields['is_set']
            return render_to_response(template,{'form':form,
                'edit_flag':True},
                context_instance=RequestContext(request))
    else:
        form = EditReplayForm()
        del form.fields['is_set']
	form.fields['hidden_syntax'].initial = replay.syntax
        for m in map:
            form.fields[m].initial = getattr(replay,m)
        if request.META.get('HTTP_REFERER',''):
            form.fields['url'].initial = request.META.get('HTTP_REFERER','/')
        return render_to_response(template,{'form':form,
            'replay_version_id': replay.version.id,
            'replay_type': replay.type,
            'replay_winners': replay.winner,
            'edit_flag': True},
            context_instance=RequestContext(request))

@login_required
@can_act
@benchmarking
def upload_replay_old(request,game):
    template = get_skin_template(request.user, 'replays/upload_replay_old.html')
    if request.method == 'POST':
        form = UploadReplayForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            type = form.cleaned_data.get('type',0)
            nonstd_layout = form.cleaned_data['nonstd_layout']
            teams = form.cleaned_data.get('teams','Just a lot of players')
            winners = form.cleaned_data['winners']
            version = form.cleaned_data['version']
            comments = form.cleaned_data['comments']
            replay_data = form.cleaned_data['replay']
            races = form.cleaned_data['races']
            is_set = form.cleaned_data['is_set']
            syntax = form.cleaned_data['hidden_syntax']
	    if is_set:
                type = 5
            if (replay_data.size/1024/1024)>5: #5mb replay
                return HttpResponseRedirect('/upload/size/overlimited')
            path = os.path.join(settings.MEDIA_ROOT,"replays/")+str(request.user.id)
            compress = False
            if not is_zip_file(replay_data): compress = True
            replay_db = save_file(replay_data, path,compress=compress)
            #already've been downloaded
            if not replay_db:
                return HttpResponseRedirect('/replay/already/downloaded')
            upload_date = datetime.now()
            r = Replay(name=name, type=type, nonstd_layout=nonstd_layout, teams = teams,
                winner = winners, version=version,comments=comments,replay=replay_db,
                #adv fields
                upload_date=datetime.now(),
                author=request.user, races=races, is_set=is_set,syntax=syntax)
            r.save()
        
        else:
            return render_to_response(template,
                {'form': form},
                context_instance=RequestContext(request,processors=[benchmark]))
    #settings overriding
    version_choices = list()
    version_choices.append((0,'---------'))
    versions = Version.objects.filter(game__short_name=game).order_by(
        '-release_number','-patch')
    for v in versions:
        msg = "%s: %s %s" % (v.game.name,v.name,v.patch)
        version_choices.append((v.id, msg))

    form = UploadReplayForm()
    form.fields['version'].choices = version_choices
    form.fields['hidden_syntax'].initial = settings.SYNTAX[0][0]
    #form.fields['version']._choices = version_choices 
    return render_to_response(template,
        {'form': form},
        context_instance=RequestContext(request,processors=[benchmark]))

@benchmarking
@update_subscription_new(app_model='files.replay',pk_field='number')
def show_replay(request, number=1,object_model='files.replay'):
    """ shows a replay, number is replays's id, object_model passes through update_subscription
    decorator to update its notification status for a selected user (request.user) """
    template_err = get_skin_template(request.user, 'replays/404.html')
    template = get_skin_template(request.user, 'replays/all.html')
    try:
        replay = Replay.objects.get(id__exact=number)
    except Replay.DoesNotExist:
        return render_to_response(template_err,
            {},
            context_instance=RequestContext(request))
    #Comments
    replay_type = ContentType.objects.get(app_label='files', model='replay')
    #Pages
    comments = Comment.objects.filter(content_type = replay_type.id, object_pk = str(replay.id))
    _pages_ = get_settings(request.user,'comments_on_page',30)
    #paginator = Paginator(comments, _pages_)
    #num_pages = paginator.num_pages
    page = request.GET.get('page',1)
    #try:
    #    comments = paginator.page(page)
    #    paginator.number = int(page)
    #except (EmptyPage, InvalidPage):
    #    comments = paginator.page(1)
    #    paginator.number = int(1)
    #links = make_links(paginator.num_pages,'')
    #links = paginator.page_range
    comments = paginate(comments,page,pages=_pages_,jump='#comments')
    """ #old, ugly and not wise code block 
    #saving comments with all validations
    #if authenticated ;)
    if hasattr(request.user,'nickname'):
        redirect = save_comment(request=request,template=template,
            vars={'replay': replay,
            'comments': comments,
            'page':comments}, #replace it withing template
            ct=replay_type,
            object_pk=str(replay.id)
        )
        #success
        if 'success' in redirect:
            if redirect['success']:
                return HttpResponseRedirect(redirect['redirect'])
            #failed
            else:
                #without comments it looks MUCH BETTER :)
                return render_to_response(template,
                    {'replay':replay,
                    'form':redirect['form'],
                    'page':comments
                    },
                    context_instance=RequestContext(request,
                        processors=[benchmark]))
    """

    form = CommentForm(request=request,initial={'app_n_model':'files.replay','obj_id': number,
    'url': request.META.get('PATH_INFO','')})
    return render_to_response(template,
        {'replay':replay,
        'comments': comments,
        'form': form,
        'page': comments
        },
        context_instance=RequestContext(request,
            processors=[pages,benchmark]))

def show_replays(request):
    template = get_skin_template(request.user,'replays/categories.html')
    games = Game.objects.all().order_by('-name')
    all = Replay.objects.all().count()
    duels = Replay.objects.filter(type='1').count()
    teams = Replay.objects.exclude(type='1').exclude(type='0').count()
    nonstds = Replay.objects.filter(type='0').count()
    stats = {
            'all': all,
            'duels': duels,
            'teams': teams,
            'nonstds': nonstds,
        }
    return render_to_response(template,
        {'stats': stats,
        'games': games},
        context_instance=RequestContext(request))

def show_categories(request,type=''):
    template = get_skin_template(request.user,'replays/categories.html')
    games = Game.objects.all().order_by('-name')
    if not type:
        all = Replay.objects.count()
        duels = Replay.objects.filter(type='1').count()
        teams = Replay.objects.exclude(type='1').exclude(type='0').count()
        nonstds = Replay.objects.filter(type='0').count()
    else:
        all = Replay.objects.all().filter(version__game__short_name=type).count()
        duels = Replay.objects.filter(type='1', version__game__short_name=type).count()
        teams = Replay.objects.exclude(type='1').filter(version__game__short_name=type).exclude(type='0').count()
        nonstds = Replay.objects.filter(type='0', version__game__short_name=type).count()
    stats = {
            'all': all,
            'duels': duels,
            'teams': teams,
            'nonstds': nonstds,
        }
    return render_to_response(template,
        {'stats': stats,
        'games': games},
        context_instance=RequestContext(request))

@csrf_protect
@benchmarking
def all_replays(request,type='',version='',patch='',gametype=''):
    template = get_skin_template(request.user, 'replays/all.html')
    page = request.GET.get('page',1)
    #if gametype:
    #    replays = Replay.objects.all().filter(type__icontains=gametype)
    if type or gametype:
        replays = Replay.objects.all().filter(type__icontains=gametype,
            version__game__short_name__iexact=type, #type shoud be checked with 'stricted logic rule'
            version__name__icontains=version,
            version__patch__icontains=patch).order_by('-id')
    else: replays = Replay.objects.all().order_by('-id')
    _pages_ = get_settings(request.user,'replays_on_page',20)
    formclass = action_formset_ng(request, replays, Replay,
        permissions=['files.delete_replay', 'files.change_replay'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(request.get_full_path())
        else:
            return direct_to_template(request, template,
                {'form': form, 'replays': replays, 'page': page},
                processors=[benchmark])
    #paginator = Paginator(replays,_pages_)
    #links = make_links(paginator.num_pages,'')
    #links = paginator.page_range
    #try:
    #    replays = paginator.page(page)
    #    paginator.number = int(page)
    #except (EmptyPage,InvalidPage):
    #    replays = paginator.page(1)
    #    paginator.number = int(1)
    form = formclass()
    replays = paginate(replays,page,pages=_pages_)
    return render_to_response(template,
        {'replays': replays,
        'page': replays, 'form': form},
        context_instance=RequestContext(request,
            processors=[benchmark]))

@csrf_protect
@benchmarking
def replays_by_author(request,nickname,game='',version='',patch=''):
    template = get_skin_template(request.user,'replays/all.html')
    user = get_object_or_404(User,nickname__exact=nickname)
    query_args = {'author':user,'version__name__icontains':version,'version__patch__icontains':patch }
    if game: query_args.update( {'version__game__short_name':game } )
    replays = Replay.objects.filter(**query_args)
    
    _pages_ = get_settings(request.user,'replays_on_page',30)
    page = int(request.GET.get('page',1))
    formclass = action_formset_ng(request, replays, Replay,
        permissions=['files.delete_replay', 'files.change_replay'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(request.get_full_path())
        else:
            return direct_to_template(request, template,
                {'form': form, 'replays': replays, 'page': page},
                processors=[benchmark])
    
    form = formclass()
    replays = paginate(replays,page,pages=_pages_)
    return render_to_response(template,{'replays':replays,'page':replays, 'form': form},
        context_instance=RequestContext(request,processors=[benchmark]))

#TODO: rewrite it, version__game__short_name=bla-bla gives an logical breaks
def category_replays(request,type='',gametype='',version='',patch=''):
    template = get_skin_template(request.user,'replays/all.html')
    #1 - duel, 0 - std, others - team
    page = request.GET.get('page',1)
    if gametype:
        if type == 1:
            replays = Replay.objects.filter(type='1', version__game__short_name=gametype,
                version__name__icontains=version,
                version__patch__icontains=patch).order_by('-id')
        elif type == 0:
            replays = Replay.objects.filter(type='0',version__game__short_name=gametype,
                version__name__icontains=version,
                version__patch__icontains=patch).order_by('-id')
        else:
            replays = Replay.objects.exclude(type='1').exclude(type='0').filter(version__game__short_name=gametype,
                version__name__icontains=version,
                version__patch__icontains=patch)
    else:
        if type == 1:
            replays = Replay.objects.filter(type='1').order_by('-id')
        elif type == 0:
            replays = Replay.objects.filter(type='0').order_by('-id')
        else:
            replays = Replay.objects.exclude(type='1').exclude(type='0')
    _pages_ = get_settings(request.user,'replays_on_page',20)
    replays = paginate(replays,page,pages=_pages_)
    return render_to_response(template,
        {'replays': replays,
        'page': replays},
        context_instance=RequestContext(request,
            processors=[pages]))

@csrf_protect
@login_required
@can_act
def upload_image(request):
    template = get_skin_template(request.user, 'gallery/upload.html')
    form = UploadImageModelForm()
    if request.method == 'POST':
        form = UploadImageForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            return HttpResponseRedirect(reverse('files:galleries'))
        else:
            return direct_to_template(request, template,
                {'form': form})
    return direct_to_template(request, template,
        {'form': form})

@csrf_protect
@login_required
def action_image(request, id, action=None):
    template = get_skin_template(request.user, 'gallery/action_image.html')
    instance = get_object_or_404(GalleryImage, id=id)
    if request.method == 'POST':
        form = ImageModelForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('files:image', args=(form.instance.pk,)))
        else:
            return direct_to_template(request, template,
                {'form': form})
    form = ImageModelForm(instance=instance)
    return direct_to_template(request, template,
        {'form': form})

@login_required
@can_act
def upload_image_old(request):
    template = get_skin_template(request.user,'gallery/upload.html')
    galleries = Gallery.objects.all()
    if not galleries:
        form = CreateGalleryForm()
        return HttpResponseRedirect('/gallery/create')

    gallery_choices = list()
    for g in galleries:
        gallery_choices.append((g.id,g.name))

    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES,request=request)
        if form.is_valid():
            from cStringIO import StringIO
            from PIL import Image
            image_file = form.cleaned_data['image']
            gallery = form.cleaned_data['gallery']
            comments = form.cleaned_data['comments']
            title = form.cleaned_data['title']
            #TODO MAKE HELPER FOR Image and Thumbnail saving
            path = "%s/images/galleries/%s" % (settings.MEDIA_ROOT, request.user.id)
            thmb_path = "%s/images/galleries/thumbnails/%s" % (settings.MEDIA_ROOT, request.user.id)
            db_path,db_thmb_path = save_thmb_image(path,thmb_path,image_file,(200,200))
            g = Gallery.objects.get(id=gallery)
            db = GalleryImage(title=title,gallery=g,image=db_path,thumbnail=db_thmb_path)
            
            if comments: db.comments = comments
            db.owner = request.user
            db.save()
        else:
            form.fields['gallery'].choices = gallery_choices
            form.fields['gallery']._choices = gallery_choices
            return render_to_response(template,
                {'form': form,},
                context_instance=RequestContext(request))
    form = UploadImageForm()
    #print gallery_choices
    #form.fields['gallery'].choices = gallery_choices
    form.fields['gallery'].choices = gallery_choices
    return render_to_response(template,
        {'form': form},
        context_instance=RequestContext(request))

@benchmarking
def show_all_images(request, id=None, action=None):
    template = get_skin_template(request, 'gallery/gallery.html')
    galleries = Gallery.objects.filter(type='global').order_by('-id')
    qset = Q(gallery__type='global')
    if id: qset = qset & Q(gallery__id=id)
    images = GalleryImage.objects.filter(qset).order_by('-id')
    page = request.GET.get('page', 1)
    _pages_ = get_settings(request.user, 'objects_on_page', 27)
    formclass = action_formset_ng(request, images, GalleryImage,
        permissions=['files.delete_image', 'files.change_image'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            #action = form.cleaned_data['action']
            #qset = form.cleaned_data['items']
            #if action == 'delete':
            #    if request.user.is_superuser or request.user.has_permissions('files.delete_images'):
            #        qset.delete()
            return HttpResponseRedirect(reverse('files:galleries'))
        else:
            return direct_to_template(request, template,
                {
                    'galleries': galleries, 'images': images,
                    'form': form
                }, processors=[benchmark]
            )
    form = formclass()
    images = paginate(images, page, pages=_pages_)
    return direct_to_template(request, template,
        {'galleries': galleries, 'images': images,
        'form': form},
        processors=[benchmark])

#ITZ FUCKING UGLY!!!!
@benchmarking
def show_all_images_old(request,id=''):
    template = get_skin_template(request.user,'gallery/gallery.html')
    try:
        page = int(request.GET.get('page',1))
    except:
        page = 1
    galleries = Gallery.objects.filter(type__exact='global').order_by('-id')
    images = GalleryImage.objects.filter(gallery__type__exact='global').order_by('-id')
    if id:
        try:
            id = int(id)
            images = images.filter(gallery__id__exact=id)
        except:
            pass
    _pages_ = get_settings(request.user,'objects_on_page',27)
    images = paginate(images,page,pages=_pages_)
    return render_to_response(template,
        {'images': images,
        'galleries': galleries,
        'page': images,
        'gallery_id': id},
        context_instance=RequestContext(request,
            processors=[pages,benchmark]))

""" USER GALLERIES
@login_required
def create_gallery(request):
    template = get_skin_template(request.user,'gallery/create.html')
    if request.method == 'POST':
        form = CreateGalleryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            owner = request.user
            nums = Gallery.objects.filter(owner=owner).count()
            if nums>3:
                return HttpResponseRedirect('/gallery/overlimited')
            try:
                check = Gallery.objects.get(name=name,owner=owner)
                return HttpResponseRedirect('/gallery/exists')
            except Gallery.DoesNotExist:
                gallery = Gallery(name=name, owner=owner)
                gallery.save()
                return HttpResponseRedirect('/gallery/created')
        else:
            return render_to_response(template,
                {'form': form},
                context_instance=RequestContext(request))
    form = CreateGalleryForm()
    return render_to_response(template,
        {'form': form},
        context_instance=RequestContext(request))
"""

@benchmarking
def show_gallery(request,gallery=1,gallery_name=None):
    template = get_skin_template(request.user,'gallery/gallery.html')
    template_err = get_skin_template(request.user,'gallery/404.html')
    gallery = int(gallery)
    try:
        if gallery_name is not None:
            g = Gallery.objects.get(name__iexact=gallery_name)
        else:
            g = Gallery.objects.get(id=gallery)
        images = GalleryImage.objects.filter(gallery=g)
        try:
            page = int(request.GET.get('page',1))
        except ValueError:
            page = 1
        _pages_ = get_settings(request.user,'objects_on_page',12)
        images = paginate(images,page,pages=_pages_)
    except:    
        return render_to_response(template_err, {},
            context_instance=RequestContext(request))
    
    return render_to_response(template,
        {'gallery': g,
        'images': images,
        'page': images},
        context_instance=RequestContext(request,
            processors=[benchmark]))

@login_required
@can_act
def action_image_old(request, id, action):
    next = ''
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            next = form.cleaned_data['url']
    can_delete = request.user.user_permissions.filter(codename='delete_images')
    try:
        img = GalleryImage.objects.get(id=id)
        img_path = img.image.path
        thmb_path = img.thumbnail.path
        #broken code FIX IT IMMIDIATELY
        if img.owner == request.user or can_delete or request.user.is_superuser\
            or request.user.is_staff:
            from os import remove as delete
            delete(thmb_path)
            delete(img_path)
            img.delete()
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect('/gallery/image/deleted')
        else:
            return HttpResponseRedirect('/gallery/images/undeletable')
    except GalleryImage.DoesNotExist:
        return HttpResponseRedirect('/gallery/image/undeletable')

@update_subscription
@user_visit(object_pk='number',ct='files.image')
def show_image(request, number=None,object_model='files.image', alias=None):
    template_err = get_skin_template(request.user, 'gallery/404.html')
    template = get_skin_template(request.user, 'gallery/image.html')
    if number:
        image = get_object_or_404(GalleryImage, id=number)
    elif alias:
        image = get_object_or_404(GalleryImage, alias__iexact=alias)
    else:
        raise Http404("No data was passed")
    #try:
    #    image = GalleryImage.objects.get(id__exact=number)
    #except GalleryImage.DoesNotExist:
    #    return render_to_response(template_err,
    #        {},
    #        context_instance=RequestContext(request))
    #
    #Comments
    image_type = ContentType.objects.get(app_label='files', model='image')
    #Pages
    comments = Comment.objects.filter(content_type = image_type.id, object_pk = str(image.id))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    page = request.GET.get('page',1)
    comments = paginate(comments,page,pages=_pages_) 
    #Form for authenticated user to leave their's comments
    form = CommentForm(request=request,initial={'app_n_model':'files.image','obj_id': number,'url':
                request.META.get('PATH_INFO','')})
    return render_to_response(template,
        {'image':image,
        'img_comments': comments,
        'form': form,
        'page': comments},
        context_instance=RequestContext(request,
            processors=[pages]))

def show_raw_image(request, alias, thumbnail=False):
    import Image
    response = HttpResponse()
    image = get_object_or_404(GalleryImage, alias__iexact=alias)
    if thumbnail:
        f = image.thumbnail.file.read()
    else:
        f = image.image.file.read()
    img = Image.open(StringIO(f))
    content_type = 'image/' + img.format.lower()
    response['Content-Type'] = content_type
    del img
    response.write(f)
    return response

@csrf_protect
@login_required
@check_user_fields({'is_staff': True})
def show_files(request):
    template = get_skin_template(request.user, 'files/files.html')
    page = request.GET.get('page',1)
    files = File.objects.all().order_by('-upload_date')
    _pages_ = get_settings(request.user,'objects_on_page',100)
    files = paginate(files,page,pages=_pages_)
    formclass = action_formset_ng(request, File.objects.all(), File,
        permissions=['files.delete_file', 'files.change_file'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'], form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(reverse('files:files'))
        else:
            return direct_to_template(request, template,
                {'files': files, 'page': files, 'form': form},
                processors=[pages])
    return render_to_response(template,
        {'files':files,
        'page': files,
        'form': formclass},
        context_instance=RequestContext(request,
            processors=[pages]))

def make_fake_files(request,model='',field=''):
    model = get_model(*model.split('.'))
    objects = model.objects.all()
    for obj in objects:
        file = getattr(obj,field)
        file_name = os.path.join(settings.MEDIA_ROOT,file.path)
        from os import stat,makedirs
        try:
            makedirs(file_name[:file_name.rindex('/')], mode=0775)
        except:
            pass
        try:
            stat(os.path.join(settings.MEDIA_ROOT,file_name))
        except OSError:
            open(file_name,'w').write('fake')
    return HttpResponseRedirect('/')
        
def make_fake_attachments(request):
    attachments = Attachment.objects.all()
    for a in attachments:
        file_name = os.path.join(settings.MEDIA_ROOT,a.attachment.path())
        #print file_name
        open(file_name,'w').write('fake')
    return HttpResponseRedirect('/')

def return_replay_from_pack(request,id=0,idx=0,compress='null'):
    referer = request.META.get('HTTP_REFERER','/') #IF SOMETHING GOES WRONG :)
    idx = int(idx)
    try:
        r = Replay.objects.get(id=id)
        if r.is_set:
            #unpack file we need
            try:
                full_filename = r.zip_info['info'][idx]['filename']
                filename = r.zip_info['info'][idx]['small_filename']
                size = r.zip_info['info'][idx]['file_size']
                compress_size = r.zip_info['info'][idx]['compress_size']
            except IndexError:
                return HttpResponseRedirect(referer)
            #implement temp directory cache
            buffer = r.replay_pack_instanse.file.read(name=full_filename)
            """if compress in 'zip':
                response = HttpResponse(mimetype='application/zip')
                response['Content-Disposition'] = 'attachment; filename=%s.zip' % (filename)
                response['Content-Length'] = compress_size
                #we should save zipfile before its retrieving 
                zip_buffer = StringIO() #make a fake file :)
                zip_buffer_instance = zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED)
                zip_buffer_instance.writestr("%s.zip" % filename,buffer)
                #return at start zip file position
                zip_buffer.seek(0)
                response.write(zip_buffer.read())
                return response
                #return HttpResponseRedirect(referer)
            """
            if compress in 'bz2':
                response = HttpResponse(mimetype='application/x-bzip')
                response['Content-Disposition'] = 'attachment; filename=%s.bz2' % (filename)
                bzdata = bz2.compress(buffer)
                response['Content-Length'] = len(bzdata)
                response.write(bzdata)
                return response
            else:
                response = HttpResponse(mimetype='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                response.write(buffer)
            return response
        else:
            return HttpResponseRedirect('/replay/does/not/set-like-pack')
    except Replay.DoesNotExist:
        return HttpResponseRedirect('/replay/does/not/exist')
    return HttpResponseRedirect(referer)

@login_required
@can_purge_replays
@can_act
def do_purge_replay(request,id):
    try:
        r = Replay.objects.get(id=id)
        #r.delete()
        return HttpResponseRedirect('/replay/purged')
    except Replay.DoesNotExist:
            return HttpResponseRedirect('/replay/does/not/exist')
"""
#TODO: OVERWRITE action_function =\
#DOES NOT WORK (not implemented yet :))
@login_required
@can_purge_replays
def purge_replay(request,id=0,approve='force'):
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            next = form.cleaned_data['url'] #from where we get here ;)
    can_purge_replays = request.user.user_permissions.filter(codename='purge_replays')
    if request.user.is_superuser or can_purge_replays:
        replay.delete()
        return HttpResponseRedirect('/replay/purged')
    else:
        return HttpResponseRedirect('/replay/does/not/exist')
"""

#O_O I do not know why but without it template render is broken
@login_required
def purge_replay(request,id=0,approve='force'):
    pass
    
def search_replay(request):
    template = get_skin_template(request.user, 'replays/search.html')
    template_found = get_skin_template(request.user, 'replays/search.html')
    
    query = request.POST.get('query','') 

    if query is None:
            request.session['search_q'] = query
    
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
    else:
        #fp = request.get_full_path()
        #r_url = reverse('apps.files.views.search_replay')
        if request.get_full_path() == reverse('files:replay-search'):
            if 'search_q' in request.session:
                del request.session['search_q']
    
    query = query or request.session.get('search_q', '')
    if query == '':
            form = SearchForm()
            return render_to_response(template,
                {'form': form},
                 context_instance=RequestContext(request))

    #q = (
    #    Q(author__nickname__icontains=query)|Q(comments__icontains=query)|
    #    Q(name__icontains=query)|Q(races__icontains=query)
    #)     
    kw_search = dict()
    q = None
    map = ['author__nickname__icontains','comments__icontains','name__icontains','races__icontains']
    for m in map: 
        kw_search[m] = query
        if not q:
                q=Q(**kw_search)
        else:
                q = q|Q(**kw_search)
        kw_search = {}
    replays = Replay.objects.filter(q)
    _pages_ = get_settings(request.user,'replays_on_page',40)
    page = request.GET.get('page',1)
    replays = paginate(replays,page,pages=_pages_) 
    form = SearchForm()
    form.fields['query'].initial = query
    return render_to_response(template_found,
        {
        'replays': replays,
        'page': replays,
        'form': form,
        'query': query},
        context_instance=RequestContext(request))

def xhr_get_replay_versions(request, id=None):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    if not id:
        response.write('[]')
        return response
    versions = Version.objects.filter(game__id=id)
    response.write(serializers.serialize("json",versions))
    return response

def xhr_get_img_alias(request, alias):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    try:
        image = GalleryImage.objects.get(alias=alias)
    except GalleryImage.DoesNotExist:
        response.write("false")
        return response
    from anyjson import serialize as serialize_json
    out = serialize_json({'alias': image.alias})
    response.write(out)
    return response
