# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import apps.tabletop.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Codex',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('title', models.CharField(verbose_name='title', max_length=128)),
                ('plain_side', models.CharField(verbose_name='plain side', max_length=128, blank=True)),
                ('revisions', models.CommaSeparatedIntegerField(verbose_name='revisions', max_length=64)),
                ('content_type', models.ForeignKey(verbose_name='content type', related_name='ct_set_for_codex', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('name', models.CharField(primary_key=True, verbose_name='Title', max_length=50, serialize=False)),
                ('codename', models.CharField(unique=True, verbose_name='Codename', max_length=15)),
            ],
            options={
                'verbose_name_plural': 'Games',
                'verbose_name': 'Game',
            },
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='Title', max_length=50)),
                ('game', models.ForeignKey(to='tabletop.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='title', max_length=100)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, verbose_name='created on')),
                ('layout', models.CharField(verbose_name='layout', max_length=30)),
                ('deployment', models.CharField(default='dow', verbose_name='deployment', choices=[('dow', 'Dawn of War'), ('ha', 'Hammer and Anvil'), ('vs', 'Vanguard Strike')], max_length=128)),
                ('comment', models.TextField(verbose_name='comment', max_length=10240)),
                ('comment_cache', models.TextField(help_text='comment rendered cache', verbose_name='comment cache', null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False, verbose_name='is approved')),
                ('is_draw', models.BooleanField(default=False, verbose_name='is draw', help_text='marks if match was finished with draw result')),
                ('syntax', models.CharField(verbose_name='syntax', choices=[('textile', 'textile'), ('bb-code', 'bb-code')], max_length=20)),
                ('mission', models.ForeignKey(verbose_name='mission', to='tabletop.Mission', null=True, blank=True)),
                ('owner', models.ForeignKey(to='accounts.User', related_name='report_owner_set')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Roster',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='title', max_length=100)),
                ('roster', models.TextField(verbose_name='roster', max_length=4096)),
                ('roster_cache', models.TextField(help_text='rendered roster cache', verbose_name='roster cache', null=True, blank=True)),
                ('comments', models.TextField(verbose_name='comments', null=True, max_length=10240, blank=True)),
                ('revision', models.IntegerField(help_text='revision means how new your codex is (bigger is newer)', verbose_name='издание кодекса', validators=[apps.tabletop.models.Roster.valid_revision])),
                ('pts', models.IntegerField(help_text='amount of codex points', verbose_name='pts')),
                ('syntax', models.CharField(verbose_name='Syntax', null=True, choices=[('textile', 'textile'), ('bb-code', 'bb-code')], blank=True, max_length=20)),
                ('wins', models.PositiveIntegerField(default=0, verbose_name='wins', blank=True)),
                ('defeats', models.PositiveIntegerField(default=0, verbose_name='defeats', blank=True)),
                ('codex', models.ForeignKey(default=1, verbose_name='codex', to='tabletop.Codex', null=True, blank=True)),
                ('owner', models.ForeignKey(to='accounts.User', related_name='roster_owner')),
            ],
            options={
                'ordering': ['-id'],
                'permissions': (('edit_anonymous_rosters', 'Can edit anonymous rosters'), ('edit_user_rosters', "Can edit another user's rosters")),
            },
        ),
        migrations.AddField(
            model_name='report',
            name='rosters',
            field=models.ManyToManyField(to='tabletop.Roster', verbose_name='rosters'),
        ),
        migrations.AddField(
            model_name='report',
            name='winners',
            field=models.ManyToManyField(to='tabletop.Roster', verbose_name='winners', null=True, related_name='breport_winners_sets', blank=True),
        ),
    ]
