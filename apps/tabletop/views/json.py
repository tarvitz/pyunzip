# coding: utf-8
from apps.core.helpers import render_to_json
from apps.tabletop.models import Roster
from apps.core.helpers import safe_ret

@render_to_json(content_type='application/json')
def roster_search(request):
    q = request.GET.get('q', '')
    # 100 queries maxium? better optimize
    if q and len(q) >= 3:
        rosters = Roster.objects.filter(title__icontains=q)[:100]
    else:
        rosters = Roster.objects.none()
    fields = ['__unicode__', 'title', 'id']
    out = []
    for roster in rosters:
        instance = {}
        for field in fields:
            instance.update({
                field.replace('__', ''): safe_ret(roster, field)
            })
        out.append(instance)
    return {
        'rosters': out
    }
