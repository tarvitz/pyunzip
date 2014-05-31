# coding: utf-8
from apps.news.models import Event
from datetime import datetime, timedelta


def weekly_events(request):
    now = datetime.now()
    #start = datetime(*now.timetuple()[:3]) - timedelta(days=now.weekday())
    #end = datetime(*now.timetuple()[:3]) + timedelta(
    #    days=6 - now.weekday(), hours=23, minutes=59)
    end = now + timedelta(weeks=1)
    new_events = Event.objects.filter(is_finished=False,
                                      date_end__lte=end)
    return {
        'new_events': new_events
    }