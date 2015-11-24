from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from django.conf import settings
admin.autodiscover()


urlpatterns = [
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
    url(r'^', include('apps.accounts.urls', namespace='accounts')),
    url(r'^', include('apps.core.urls', namespace='core')),
    url(r'^', include('apps.wh.urls', namespace='wh')),
    url(r'^', include('apps.files.urls', namespace='files')),
    url(r'^', include('apps.news.urls', namespace='news')),
    url(r'^', include('apps.tabletop.urls', namespace='tabletop')),
    url(r'^', include('apps.karma.urls', namespace='karma')),
    url(r'^', include('apps.comments.urls', namespace='comments')),
    url(r'^', include('apps.pybb.urls', namespace='pybb')),
    url('^search/', include('haystack.urls')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]


if settings.DEV_SERVER:
    urlpatterns += [
        url(r'^uploads/(?P<path>.*)$', serve,
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }),
    ]
