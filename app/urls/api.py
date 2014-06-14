from .urls import urlpatterns

from django.conf.urls import url, include, patterns

from apps.accounts.views.api import (
    UserViewSet, PMViewSet, PolicyWarningViewSet
)
from apps.news.views.api import EventViewSet
from apps.comments.views.api import CommentWatchViewSet
from apps.tabletop.views.api import RosterViewSet, CodexViewSet

from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'pms', PMViewSet)
router.register(r'warnings', PolicyWarningViewSet)
router.register(r'events', EventViewSet)
router.register(r'commentwatch', CommentWatchViewSet)
router.register(r'rosters', RosterViewSet)
router.register(r'codexes', CodexViewSet)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(router.urls, namespace='api')),
)