# coding: utf-8
from datetime import datetime

from django_cron import CronJobBase, Schedule
from apps.accounts.models import PolicyWarning
from django.db.models import Q


class PolicyWarningsMarkExpireCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:01', '00:15', ]

    schedule = Schedule(
        run_at_times=RUN_AT_TIMES,
    )
    code = 'accounts.policy_warnings_mark_as_expired'

    def do(self):
        now = datetime.now()
        qset = (
            Q(date_expired__lt=now)
        )
        PolicyWarning.objects.filter(qset).update(is_expired=True)