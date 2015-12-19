# coding: utf-8
from datetime import timedelta
from django.db import models
from uuid import uuid1

from django.utils import timezone


class UserSIDManager(models.Manager):
    def create(self, user):
        sid = uuid1().hex

        if not user:
            return None

        expired_date = timezone.now() + timedelta(days=1)
        instance = self.model(user=user, sid=sid, expired_date=expired_date,
                              expired=False)
        instance.save()
        return instance
