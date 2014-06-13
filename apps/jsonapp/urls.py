from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^wh/', include('apps.wh.urls.json', namespace='wh')),
    url(r'^', include('apps.files.urls.json', namespace='files')),
    url(r'^', include('apps.tabletop.urls.json', namespace='tabletop')),
    url(r'^karma/', include('apps.karma.urls.json', namespace='karma')),
)
