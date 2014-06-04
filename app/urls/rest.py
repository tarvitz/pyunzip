from .urls import urlpatterns

from django.conf.urls import url, include, patterns

from apps.accounts.views.rest import UserViewSet
from apps.news.views.rest import EventViewSet
from apps.comments.views.rest import CommentWatchViewSet
from apps.tabletop.views.rest import RosterViewSet, CodexViewSet

from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'events', EventViewSet)
router.register(r'commentwatch', CommentWatchViewSet)
router.register(r'rosters', RosterViewSet)
router.register(r'codexes', CodexViewSet)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(router.urls, namespace='api')),
)