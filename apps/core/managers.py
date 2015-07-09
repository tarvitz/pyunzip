# coding: utf-8

from datetime import datetime, timedelta
from django.db import models
from uuid import uuid1


class UserSIDManager(models.Manager):
    def create(self, user):
        sid = uuid1().hex

        if not user:
            return None

        expired_date = datetime.now() + timedelta(days=1)
        instance = self.model(user=user, sid=sid, expired_date=expired_date)
        instance.save()
        return instance
