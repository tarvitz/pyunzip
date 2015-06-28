# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import apps.news.models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedNews',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='title', max_length=255)),
                ('author', models.CharField(verbose_name='author', max_length=255)),
                ('editor', models.CharField(verbose_name='editor', max_length=255, blank=True)),
                ('url', models.CharField(verbose_name='original URL', max_length=200, blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('cache_content', models.TextField(null=True, verbose_name='cache content', blank=True)),
                ('date', models.DateTimeField(verbose_name='dateTime', default=datetime.datetime.now)),
                ('approved', models.BooleanField(verbose_name='approved', default=False)),
                ('author_ip', models.CharField(verbose_name='author ip address', max_length=16, blank=True)),
                ('is_event', models.BooleanField(verbose_name='is event', default=False)),
                ('syntax', models.CharField(null=True, verbose_name='Syntax', choices=[('textile', 'textile'), ('bb-code', 'bb-code')], max_length=20, blank=True)),
                ('reason', models.CharField(null=True, verbose_name='reason', max_length=1024, blank=True)),
                ('status', models.CharField(choices=[('approved', 'approved'), ('rejected', 'rejeceted'), ('queued', 'queued'), ('revision', 'revision')], max_length=32, default='queued')),
                ('resend', models.BooleanField(help_text='marks if news notification should resend', verbose_name='resend', default=False)),
                ('attachment', models.ForeignKey(to='files.Attachment', null=True, blank=True)),
            ],
            options={
                'permissions': (('edit_archived_news', 'Can edit archived news'),),
                'verbose_name': 'Archived Article',
                'ordering': ['-id'],
                'verbose_name_plural': 'Archived News',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Category', max_length=100)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(help_text='event title', verbose_name='title', max_length=256)),
                ('content', models.TextField(help_text='content event text, description, further manual and so on', verbose_name='content')),
                ('content_html', models.TextField(help_text='rendered html content', null=True, verbose_name='content html', blank=True)),
                ('date_start', models.DateTimeField(help_text='when event date starts', verbose_name='date start')),
                ('date_end', models.DateTimeField(help_text='when event date ends', null=True, verbose_name='date end', blank=True)),
                ('type', models.CharField(verbose_name='type', choices=[('game', 'Game'), ('tournament', 'Tournament'), ('order', 'Order'), ('pre-release', 'Pre-release'), ('release', 'Release'), ('festivity', 'Festivity')], max_length=16, default='game')),
                ('league', models.CharField(help_text='game league', null=True, verbose_name='league', choices=[('wh40k', 'Warhammer 40000'), ('whfb', 'Warhammer fantasy battle'), ('mtg', 'Magic the gathering'), ('board', 'Board gaming'), ('dnd', 'Dungeons and Dragons')], max_length=32, blank=True, default='wh40k')),
                ('is_finished', models.BooleanField(verbose_name='is finished', default=False)),
                ('is_all_day', models.BooleanField(help_text='marks if event could place whole day', verbose_name='is all day', default=False)),
                ('participants', models.ManyToManyField(help_text='participants would take a part in the event', null=True, to=settings.AUTH_USER_MODEL, related_name='event_users_sets', blank=True)),
            ],
            options={
                'verbose_name': 'Event',
                'ordering': ['is_finished', 'date_start'],
                'verbose_name_plural': 'Events',
            },
        ),
        migrations.CreateModel(
            name='EventPlace',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(help_text='event place title', verbose_name='title', max_length=512)),
                ('address', models.CharField(help_text='event place address', null=True, verbose_name='address', max_length=1024, blank=True)),
                ('contacts', models.CharField(help_text='contacts/help who to find it', null=True, verbose_name='contacts', max_length=256, blank=True)),
            ],
            options={
                'verbose_name': 'Event Place',
                'verbose_name_plural': 'Event Places',
            },
        ),
        migrations.CreateModel(
            name='EventWatch',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(verbose_name='created on', default=datetime.datetime.now)),
                ('event', models.ForeignKey(to='news.Event', verbose_name='event', related_name='event_watch_set')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='user', related_name='event_watch_user_set')),
            ],
            options={
                'verbose_name': 'Event watch',
                'verbose_name_plural': 'Event watches',
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='title', max_length=255)),
                ('author', models.CharField(verbose_name='author', max_length=255)),
                ('editor', models.CharField(verbose_name='editor', max_length=255, blank=True)),
                ('url', models.CharField(verbose_name='original URL', max_length=200, blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('cache_content', models.TextField(null=True, verbose_name='cache content', blank=True)),
                ('date', models.DateTimeField(verbose_name='dateTime', default=datetime.datetime.now)),
                ('approved', models.BooleanField(verbose_name='approved', default=False)),
                ('author_ip', models.CharField(verbose_name='author ip address', max_length=16, blank=True)),
                ('is_event', models.BooleanField(verbose_name='is event', default=False)),
                ('syntax', models.CharField(null=True, verbose_name='Syntax', choices=[('textile', 'textile'), ('bb-code', 'bb-code')], max_length=20, blank=True)),
                ('reason', models.CharField(null=True, verbose_name='reason', max_length=1024, blank=True)),
                ('status', models.CharField(choices=[('approved', 'approved'), ('rejected', 'rejeceted'), ('queued', 'queued'), ('revision', 'revision')], max_length=32, default='queued')),
                ('resend', models.BooleanField(help_text='marks if news notification should resend', verbose_name='resend', default=False)),
                ('attachment', models.ForeignKey(to='files.Attachment', null=True, blank=True)),
                ('category', models.ForeignKey(to='news.Category')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='owner', related_name='news', default=1)),
            ],
            options={
                'permissions': (('edit_news', 'Can edit news'), ('del_restore_comments', 'Can delete and restore comments'), ('edit_comments', 'Can edit comments'), ('purge_comments', 'Can purge comments')),
                'verbose_name': 'Article',
                'verbose_name_plural': 'News',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_on', models.DateTimeField(help_text='date time when instance was created', verbose_name='created on', default=datetime.datetime.now)),
                ('expired_on', models.DateTimeField(help_text='date when note is expired', verbose_name='expired on', default=apps.news.models.Note.note_expired_on)),
                ('content', models.TextField(help_text='content', verbose_name='content')),
                ('for_authenticated_only', models.BooleanField(help_text='for authenticated users only', verbose_name='for authenticated only', default=False)),
                ('sign', models.BooleanField(help_text='if the purity seal should be with its note', verbose_name='sign')),
                ('type', models.CharField(choices=[('success', 'success'), ('info', 'info'), ('alert', 'alert'), ('warning', 'warning'), ('default', 'default')], max_length=64, default='success')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(to='news.EventPlace', null=True, verbose_name='event place', related_name='event_place_set', blank=True),
        ),
        migrations.AddField(
            model_name='archivednews',
            name='category',
            field=models.ForeignKey(to='news.Category'),
        ),
        migrations.AddField(
            model_name='archivednews',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='owner', related_name='archivednews', default=1),
        ),
        migrations.AlterUniqueTogether(
            name='eventwatch',
            unique_together=set([('event', 'user')]),
        ),
    ]
