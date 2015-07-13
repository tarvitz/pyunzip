from django.conf.urls import url, patterns
from django.contrib.auth.decorators import login_required

from apps.files.views import views

urlpatterns = patterns(
    'apps.files.views.views',
    url(r'^galleries/$', views.GalleryListView.as_view(), name='galleries'),
    url(r'^galleries/(?P<pk>\d+)/$', views.GalleryListView.as_view(),
        name='galleries'),

    url('^galleries/images/(?P<pk>\d+)/$',
        views.GalleryImageDetailView.as_view(), name='image'),
    url(r'^galleries/images/upload/$',
        login_required(views.GalleryImageCreateView.as_view()),
        name='image-upload'),
    url(r'^galleries/images/(?P<pk>\d+)/delete/$',
        login_required(views.GalleryImageDeleteView.as_view()),
        name='image-delete'),
    url(r'^images/(?P<pk>\d+)/edit/$',
        login_required(views.GalleryImageUpdateView.as_view()),
        name='image-edit'),
    url(r'^files/upload/new/$', 'file_upload', name='file-upload'),

    # todo: refactor
    url(r'^users/files/$', 'files', name='files'),
    url(r'^users/files/(?P<pk>\d+)/delete/$', 'file_delete',
        name='file-delete')
)
