from django.shortcuts import redirect
from django.views import generic

from apps.comments.forms import CommentForm
from apps.comments.models import CommentWatch
from apps.comments.forms import CommentWatchSubscribeForm
from apps.core.helpers import get_object_or_404, get_object_or_None
from apps.helpers.diggpaginator import DiggPaginator as Paginator

from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.conf import settings
# Create your views here.


class CommentCreateView(generic.CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_form.html'

    def get_success_url(self, form):
        addon = '?page=%s' % 'last'
        if hasattr(form.instance.content_object, 'get_absolute_url'):
            return form.instance.content_object.get_absolute_url() + addon
        return redirect((form.cleaned_data['url'] or '/') + addon)

    def form_valid(self, form):
        form.instance.site_id = 1
        form.instance.user = self.request.user
        # attach new comment to last comment if this comment is own
        # by current request user, else save as new
        comments = Comment.objects.filter(
            content_type=form.cleaned_data['content_type'],
            object_pk=form.cleaned_data['object_pk']
        ).order_by('-submit_date')
        if comments.count() and comments[0].user == self.request.user:
            comment = comments[0]
            comment.comment += '\n' + form.cleaned_data['comment']
            comment.save()
        else:
            form.save()
        return redirect(self.get_success_url(form))


class CommentUpdateView(generic.UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_form.html'

    def get_form_kwargs(self):
        kwargs = super(CommentUpdateView, self).get_form_kwargs()
        kwargs.update({
            'initial': {
                'url': self.request.META.get('HTTP_REFERER', '/')
            }
        })
        return kwargs

    def get_success_url(self, form):
        form.save()
        if hasattr(self.get_object().content_object, 'get_absolute_url'):
            return self.get_object().content_object.get_absolute_url()
        return form.cleaned_data.get('url', '/')

    def form_valid(self, form):
        return redirect(self.get_success_url(form))


class SubscribeCommentWatchView(generic.FormView):
    """
    Subscribe user for further comments updates
    """
    model = CommentWatch
    form_class = CommentWatchSubscribeForm
    template_name = 'comments/subscribe_form.html'

    def get_content_object(self):
        if hasattr(self, '_content_object'):
            return self._content_object
        content_type = get_object_or_404(
            ContentType, pk=self.kwargs.get('content_type', 0))
        self._content_object = get_object_or_404(
            content_type.model_class(), pk=self.kwargs.get('object_pk', 0)
        )
        return self._content_object

    def get_context_data(self, **kwargs):
        context = super(SubscribeCommentWatchView, self).get_context_data(
            **kwargs)

        context.update({
            'object': self.get_content_object()
        })
        return context

    def get_success_url(self):
        obj = self.get_content_object()
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return reverse('comments:subscribed')

    def get_form_kwargs(self):
        content_type = self.kwargs.get('content_type', 0)
        object_pk = self.kwargs.get('object_pk', 0)

        instance = get_object_or_None(CommentWatch,
                                      content_type=content_type,
                                      object_pk=object_pk)
        initial = {
            'content_type': content_type,
            'object_pk': object_pk
        }
        kwargs = super(SubscribeCommentWatchView, self).get_form_kwargs()
        kwargs.update({'initial': initial, 'instance': instance})
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_disabled = False
        comments = Comment.objects.filter(
            content_type=self.kwargs.get('content_type', 0),
            object_pk=self.kwargs.get('object_pk', 0)).order_by('-submit_date')
        if comments.count():
            form.instance.comment = comments[0]
        form.save()
        return redirect(self.get_success_url())


class CommentWatchListView(generic.ListView):
    model = CommentWatch
    paginate_by = settings.OBJECTS_ON_PAGE
    paginator_class = Paginator
    template_name = 'comments/comment_watch_list.html'

    def get_queryset(self):
        qs = super(CommentWatchListView, self).get_queryset()
        return qs.filter(user=self.request.user,
                         is_disabled=False)