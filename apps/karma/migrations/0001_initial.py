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
            name='Karma',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('comment', models.CharField(verbose_name='Comment', max_length=512, blank=True)),
                ('value', models.IntegerField(verbose_name='Power')),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Date')),
                ('url', models.URLField(verbose_name='URL', null=True, blank=True)),
                ('user', models.ForeignKey(verbose_name='user', related_name='karma_user_set', to=settings.AUTH_USER_MODEL)),
                ('voter', models.ForeignKey(verbose_name='voter', related_name='karma_voter_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
