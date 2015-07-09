from django.conf.urls import patterns


urlpatterns = patterns(
    'apps.tabletop.views',
)

urlpatterns += patterns(
    'apps.tabletop.views.json',
)
