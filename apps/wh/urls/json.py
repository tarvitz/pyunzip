from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'apps.wh.views.json',
    # old migrated
    url('^miniquote/$', 'miniquote',
        name='miniquote'),
    url(r'^armies/$', 'army',
        name='armies'),
    url(r'^armies/(?P<id>\d+)/$', 'army',
        name='armies'),
    #
    url(r'^expression/$', 'expression',
        name='expression'),
)
