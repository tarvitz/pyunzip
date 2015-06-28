# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HMenuItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='title', max_length=256)),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order', help_text='Less is prior')),
                ('attrs', models.CharField(verbose_name='attributes', null=True, max_length=1024, blank=True)),
                ('url', models.CharField(verbose_name='URL', null=True, max_length=256, blank=True)),
                ('is_hidden', models.BooleanField(default=False, verbose_name='is hidden', help_text='marks menu item as hidden')),
            ],
            options={
                'verbose_name_plural': 'Horizontal Menus',
                'verbose_name': 'Horizontal Menu',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='VMenuItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='Title', max_length=256)),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order', help_text='Less is prior')),
                ('attrs', models.CharField(verbose_name='attributes', null=True, max_length=1024, blank=True)),
                ('url', models.CharField(verbose_name='URL', null=True, max_length=256, blank=True)),
                ('is_url', models.BooleanField(default=True, verbose_name='is url?')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='is hidden', help_text='marks menu item as hidden')),
                ('parent', models.ForeignKey(related_name='children', to='menu.VMenuItem', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Vertical Menus',
                'verbose_name': 'Vertical Menu',
                'ordering': ['is_url', 'order', 'id'],
            },
        ),
    ]
