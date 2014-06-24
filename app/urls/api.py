from .urls import urlpatterns

from django.conf.urls import url, include, patterns

from apps.accounts.views.api import (
    UserViewSet, PMViewSet, PolicyWarningViewSet
)
from apps.news.views.api import EventViewSet
from apps.comments.views.api import CommentWatchViewSet, CommentViewSet
from apps.tabletop.views.api import (
    RosterViewSet, CodexViewSet, ReportViewSet, MissionViewSet, GameViewSet)
from apps.karma.views.api import KarmaViewSet
from apps.wh.views.api import (
    UniverseViewSet, FractionViewSet, SideViewSet, ArmyViewSet,
    RankTypeViewSet, RankViewSet, ExpressionViewSet, MiniQuoteViewSet)

from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'pms', PMViewSet)
router.register(r'warnings', PolicyWarningViewSet)

router.register(r'events', EventViewSet)
router.register(r'commentwatch', CommentWatchViewSet)
router.register(r'comments', CommentViewSet)

router.register(r'rosters', RosterViewSet)
router.register(r'codexes', CodexViewSet)
router.register(r'karmas', KarmaViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'games', GameViewSet)
router.register(r'missions', MissionViewSet)

router.register(r'universes', UniverseViewSet)
router.register(r'fractions', FractionViewSet)
router.register(r'sides', SideViewSet)
router.register(r'armies', ArmyViewSet)
router.register(r'ranks', RankViewSet)
router.register(r'ranktypes', RankTypeViewSet)
router.register(r'expressions', ExpressionViewSet)
router.register(r'miniquotes', MiniQuoteViewSet)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(router.urls, namespace='api')),
)