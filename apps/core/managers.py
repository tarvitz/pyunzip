# coding: utf-8

from django.db import models
from uuid import uuid1


class UserSIDManager(models.Manager):
    def create(self, user):
        sid = uuid1().hex
        
        if not user:
            return None

        instance = self.model(user=user, sid=sid)
        instance.save()
        return instance
