from django.conf.urls.defaults import *
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns('apps.farseer.views', 
    url('^non40k/l4d2/stat/$','l4d2_stat',
        name='url_non40k_l4d2stat'),
)

