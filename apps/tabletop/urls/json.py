from django.conf.urls import patterns, url


urlpatterns = patterns(
    'apps.tabletop.views',
)

urlpatterns += patterns(
    'apps.tabletop.views.json',
)
