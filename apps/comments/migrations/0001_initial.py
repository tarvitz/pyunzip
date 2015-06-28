# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('user_name', models.CharField(verbose_name="user's name", max_length=50, blank=True)),
                ('user_email', models.EmailField(verbose_name="user's email address", max_length=254, blank=True)),
                ('user_url', models.URLField(verbose_name="user's URL", blank=True)),
                ('comment', models.TextField(verbose_name='comment', max_length=3000)),
                ('submit_date', models.DateTimeField(default=None, verbose_name='date/time submitted')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address', unpack_ipv4=True, null=True, blank=True)),
                ('is_public', models.BooleanField(default=True, verbose_name='is public', help_text='Uncheck this box to make the comment effectively disappear from the site.')),
                ('is_removed', models.BooleanField(default=False, verbose_name='is removed', help_text='Check this box if the comment is inappropriate. A "This comment has been removed" message will be displayed instead.')),
                ('syntax', models.CharField(verbose_name='Syntax', null=True, choices=[('textile', 'textile'), ('bb-code', 'bb-code')], blank=True, max_length=50)),
                ('cache_comment', models.TextField(verbose_name='cache comment', null=True, blank=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', related_name='content_type_set_for_comment', to='contenttypes.ContentType')),
                ('site', models.ForeignKey(to='sites.Site')),
                ('user', models.ForeignKey(verbose_name='user', related_name='comment_comments', to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'comments',
                'verbose_name': 'comment',
                'ordering': ('submit_date',),
                'permissions': [('can_moderate', 'Can moderate comments')],
                'db_table': 'django_comments',
            },
        ),
        migrations.CreateModel(
            name='CommentWatch',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('object_pk', models.PositiveIntegerField(verbose_name='object pk')),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, verbose_name='created on')),
                ('is_disabled', models.BooleanField(default=False, verbose_name='is disabled', help_text='marks if watch is disabled for present moment')),
                ('is_updated', models.BooleanField(default=False, verbose_name='is updated', help_text='marks if comment watch was updated for new comments')),
                ('comment', models.ForeignKey(verbose_name='comment', related_name='comment_watch_set', to='comments.Comment', null=True, blank=True)),
                ('content_type', models.ForeignKey(verbose_name='content type', related_name='content_type_set_for_commentwatch', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name='user', related_name='comment_watch_user_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Comment watches',
                'verbose_name': 'Comment watch',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentwatch',
            unique_together=set([('content_type', 'object_pk', 'user')]),
        ),
    ]
