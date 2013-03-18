from django.conf.urls import *

urlpatterns = patterns('',

    (r'^quote/(?P<quote_id>\d+)/approve/$', 'apps.quotes.admin.views.approve'), #, {'document_root': settings.PATH_TO_SOMETHING_STATIC}),

)