# Create your views here.
# coding: utf-8

from django.db.models import Sum
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
User = get_user_model()

from django.views import generic
from django.core.urlresolvers import reverse_lazy

from apps.helpers.diggpaginator import DiggPaginator as Paginator

from apps.files.forms import (
    UploadFileForm, GalleryImageForm, GalleryImageUpdateForm)

from apps.files.models import Gallery, UserFile
from apps.files.models import Image as GalleryImage

from apps.core.helpers import (
    render_to, render_to_json, get_int_or_zero
)

from django.conf import settings
from apps.core.helpers import paginate
from django.shortcuts import get_object_or_404


@render_to_json(content_type='application/json')
def file_upload(request):
    form = UploadFileForm(
        request.POST or None,
        request.FILES or None,
        request=request
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'success': True,
                'file': form.instance.file,
                'thumbnail': form.cleaned_data.get('thumbnail', {}),
                'mime_type': form.instance.plain_type
            }
    return {
        'success': False,
        'form': form
    }


@login_required
@render_to('files/user_files.html')
def files(request, nickname=''):
    user_files = request.user.files.all().order_by('-id')
    page = get_int_or_zero(request.GET.get('page', 1))

    pictures = paginate(
        user_files.filter(plain_type__icontains='image'),
        page,
        pages=settings.OBJECTS_ON_PAGE
    )
    user_files = paginate(user_files, page, pages=settings.OBJECTS_ON_PAGE)

    space_used = request.user.files.aggregate(Sum('size'))
    space_used = space_used.items()[0][1] or 0

    return {
        'files': user_files,
        'pictures': pictures,
        'space_used': space_used
    }


@login_required
@render_to('files/user_files.html')
def file_delete(request, pk, nickname=''):
    user_file = get_object_or_404(UserFile, pk=pk)
    user_file.delete()
    return {
        'redirect': 'files:files'
    }


class GalleryListView(generic.ListView):
    model = GalleryImage
    template_name = 'files/gallery/gallery_list.html'
    paginate_by = settings.OBJECTS_ON_PAGE
    paginator_class = Paginator

    def get_queryset(self):
        pk = self.kwargs.get('pk', 0)
        if pk:
            return super(GalleryListView, self).get_queryset().filter(
                gallery__pk=pk)
        return super(GalleryListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(GalleryListView, self).get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 0)
        if pk:
            context.update({'gallery': get_object_or_404(Gallery, pk=pk)})
        return context


class GalleryImageDetailView(generic.DetailView):
    model = GalleryImage
    template_name = 'files/gallery/gallery_image.html'

    def get_context_data(self, **kwargs):
        context = super(GalleryImageDetailView, self).get_context_data(
            **kwargs)
        page = get_int_or_zero(self.request.GET.get('page', 1)) or 1
        comments = paginate(self.object.comment_objects.all(), page,
                            pages=settings.OBJECTS_ON_PAGE)
        context.update({'comments': comments})
        return context


class GalleryImageCreateView(generic.CreateView):
    model = GalleryImage
    template_name = 'files/gallery/gallery_image_form.html'
    form_class = GalleryImageForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(GalleryImageCreateView, self).form_valid(form)


class GalleryImageOwnerMixin(object):
    def get_queryset(self):
        qs = super(GalleryImageOwnerMixin, self).get_queryset()
        if self.request.user.has_perm('files.change_image'):
            return qs
        return qs.filter(owner=self.request.user)


class GalleryImageUpdateView(GalleryImageOwnerMixin, generic.UpdateView):
    model = GalleryImage
    template_name = 'files/gallery/gallery_image_form.html'
    form_class = GalleryImageUpdateForm


class GalleryImageDeleteView(GalleryImageOwnerMixin, generic.DeleteView):
    model = GalleryImage
    template_name = 'files/gallery/gallery_image_form.html'
    success_url = reverse_lazy('files:galleries')
