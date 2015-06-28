# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSID',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('sid', models.CharField(unique=True, verbose_name='SID', max_length=512)),
                ('expired_date', models.DateTimeField(default=datetime.datetime(2015, 7, 5, 14, 36, 1, 161042), verbose_name='Expires')),
                ('expired', models.BooleanField(default=False, verbose_name='expired?')),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, verbose_name='created on')),
                ('updated_on', models.DateTimeField(verbose_name='updated on', auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user_sid_set')),
            ],
            options={
                'verbose_name_plural': 'UserSIDs',
                'verbose_name': 'UserSID',
            },
        ),
    ]
