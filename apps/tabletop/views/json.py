# coding: utf-8
from apps.core.helpers import render_to_json
from apps.tabletop.models import Roster

@render_to_json(content_type='application/json')
def roster_search(request):
    q = request.GET.get('q', '')
    # 100 queries maxium? better optimize
    if q and len(q) >= 3:
        rosters = Roster.objects.filter(title__icontains=q)[:100]
    else:
        rosters = Roster.objects.none()

    return {
        'rosters': rosters
    }
