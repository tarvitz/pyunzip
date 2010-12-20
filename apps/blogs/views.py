# Create your views here.

from apps.core.decorators import null_function
from apps.core import get_skin_template
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from apps.blogs.models import Post
from apps.core.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from datetime import datetime
from django.http import HttpResponseRedirect
from django.core.paginator import EmptyPage,InvalidPage
from django.shortcuts import render_to_response
from django.template import RequestContext

#OBSOLETE
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.tagging.models import TaggedItem,Tag
from apps.core.helpers import get_settings,save_comment,paginate
from apps.core.decorators import update_subscription_new,benchmarking
from apps.core import benchmark

@benchmarking
def blog_index(request):
    template = get_skin_template(request.user,'blog_index.html')
    if request.user.is_staff:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(approved=True)
    page = request.GET.get('page',1)
    _pages_ = get_settings(request.user,'news_on_page',20)
    posts = paginate(posts,page,pages=_pages_)
    return render_to_response(template,{'posts':posts},
        context_instance=RequestContext(request,processors=[benchmark]))

@benchmarking
@update_subscription_new(app_model='blogs.post')
def show_post(request,id,object_model='blogs.post'):
    template = get_skin_template(request.user,'blog_index.html')
    try:
        post = Post.objects.get(id__iexact=id)
    except Post.DoesNotExist:
        return request.META.get('HTTP_REFERER','/')
    
    ct = ContentType.objects.get(app_label='blogs',model='post')
    raw_comments = Comment.objects.filter(content_type=ct,object_pk=str(id))
    page = request.GET.get('page',1)
    _pages_ = get_settings(request.user,'comments_on_page',30)
    comments = paginate(raw_comments,page,pages=_pages_,jump='#comments')
    #saves comment with all validation
    if hasattr(request.user,'nickname'):
        redirect = save_comment(request=request,template=template,
            vars={
                'p':post,
                'comments':comments,
            },
            ct=ct,object_pk=str(post.id)
        )
        if 'success' in redirect:
            if redirect['success']:
                return HttpResponseRedirect(redirect['redirect'])
            else:
                return render_to_response(template,
                    {'p':post,
                    'form':redirect['form']},
                    context_instance=RequestContext(request,
                        processors=[benchmark]))

    form = CommentForm()
    return render_to_response(template,{'p':post,'form':form,'comments':comments},
        context_instance=RequestContext(request,processors=[benchmark]))

#@null_function
@benchmarking
def get_posts_via_tag(request,tag_id):
    template = get_skin_template(request.user,'blog_index.html')
    try:
        tag = Tag.objects.get(id=tag_id)
        posts = Post.objects.filter(tags__icontains=tag.name)
        _pages_ = get_settings(request.user,'news_on_page',20)
        page = request.GET.get('page',1)
        posts = paginate(posts,page,pages=_pages_)

        if len(posts.object_list) == 0:
            return HttpResponseRedirect('/posts/does/not/exist')
    except Tag.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    return render_to_response(template,{'posts':posts},
        context_instance=RequestContext(request,processors=[benchmark]))
