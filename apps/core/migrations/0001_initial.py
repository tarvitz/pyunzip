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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sid', models.CharField(max_length=512, verbose_name='SID', unique=True)),
                ('expired_date', models.DateTimeField(verbose_name='Expires')),
                ('expired', models.BooleanField(verbose_name='expired?', default=False)),
                ('created_on', models.DateTimeField(verbose_name='created on', auto_now_add=True)),
                ('updated_on', models.DateTimeField(verbose_name='updated on', default=datetime.datetime.now)),
                ('user', models.ForeignKey(related_name='user_sid_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserSID',
                'verbose_name_plural': 'UserSIDs',
            },
        ),
    ]
