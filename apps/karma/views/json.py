# coding: utf-8
from apps.core.helpers import (
    render_to_json, get_object_or_None
)
from apps.karma.models import KarmaStatus


@render_to_json(content_type='application/json')
def karma_status(request, codename):
    status = get_object_or_None(KarmaStatus, codename__iexact=codename)
    return status
