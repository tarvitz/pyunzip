# coding: utf-8
from django.db.models import Q
from apps.news.models import Event, Note
from datetime import datetime, timedelta


def weekly_events(request):
    now = datetime.now()
    end = now + timedelta(weeks=1)
    new_events = Event.objects.filter(is_finished=False,
                                      date_end__lte=end)

    return {
        'new_events': new_events,
    }


def notes(request):
    qset = Q(
        expired_on__gte=datetime.now(),
    )
    if request.user.is_anonymous():
        qset &= Q(for_authenticated_only=False)

    return {
        'notes': Note.objects.filter(qset)
    }
