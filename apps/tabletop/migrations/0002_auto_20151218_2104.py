# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 21:04
from __future__ import unicode_literals

import apps.tabletop.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tabletop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='winners',
            field=models.ManyToManyField(blank=True, related_name='breport_winners_sets', to='tabletop.Roster', verbose_name='winners'),
        ),
        migrations.AlterField(
            model_name='roster',
            name='revision',
            field=models.IntegerField(help_text='revision means how new your codex is (bigger is newer)', validators=[apps.tabletop.models.Roster.valid_revision], verbose_name='codex revision'),
        ),
    ]
