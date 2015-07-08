# coding: utf-8
from datetime import datetime

from django_cron import CronJobBase, Schedule
from apps.news.models import Event
from django.db.models import Q


class EventsMarkFinishedCronJob(CronJobBase):
    RUN_AT_TIMES = ['23:59', '00:15', ]

    schedule = Schedule(
        run_at_times=RUN_AT_TIMES,
    )
    code = 'news.events_mark_as_finished'

    def do(self):
        now = datetime.now()
        qset = (
            Q(date_end__lt=now)
        )
        Event.objects.filter(qset).update(is_finished=True)
