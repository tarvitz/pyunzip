# coding: utf-8
from datetime import datetime
from django_cron import CronJobBase, Schedule
from apps.pybb.models import Poll


class UpdatePollJob(CronJobBase):
    """ update poll fields once a day """
    RUN_AT_TIMES = ['23:59', ]
    code = 'pybb.update_poll_expire'
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    def do(self):
        now = datetime.now()
        Poll.objects.filter(date_expire__lte=now).update(is_finished=True)