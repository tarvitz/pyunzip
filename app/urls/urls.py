from django.conf.urls import url, include, patterns
from django.contrib import admin
admin.autodiscover()
from django.conf import settings

urlpatterns = patterns(
    '',
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', admin.site.urls),
    (r'^', include('apps.accounts.urls', namespace='accounts')),
    (r'^', include('apps.core.urls', namespace='core')),
    (r'^', include('apps.wh.urls', namespace='wh')),
    (r'^', include('apps.files.urls', namespace='files')),
    (r'^', include('apps.news.urls', namespace='news')),
    (r'^', include('apps.tabletop.urls', namespace='tabletop')),
    (r'^', include('apps.karma.urls', namespace='karma')),
    (r'^', include('apps.comments.urls', namespace='comments')),
    (r'^', include('apps.pybb.urls', namespace='pybb')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)


if settings.DEV_SERVER:
    urlpatterns += patterns(
        '',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }),
    )
