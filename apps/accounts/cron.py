# coding: utf-8
from datetime import datetime
from django.utils import timezone

from django_cron import CronJobBase, Schedule
from django.db.models import Q

from . import models
from apps.core.models import UserSID


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
        models.PolicyWarning.objects.filter(qset).update(is_expired=True)


class UserSIDMarkExpireCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:01', ]

    schedule = Schedule(
        run_at_times=RUN_AT_TIMES,
    )
    code = 'accounts.usersid_mark_expired'

    def do(self):
        now = timezone.now()
        qset = (
            Q(expired_date__lte=now)
        )
        UserSID.objects.filter(qset).update(expired=True)
