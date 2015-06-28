# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousPost',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('session_key', models.CharField(verbose_name='Session key', max_length=40)),
                ('created', models.DateTimeField(verbose_name='Created', auto_now_add=True)),
                ('markup', models.CharField(default='', verbose_name='Markup', max_length=15, blank=True)),
                ('body', models.TextField(default='', verbose_name='Message', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Anonymous posts',
                'verbose_name': 'Anonymous post',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=80)),
                ('position', models.IntegerField(default=0, verbose_name='Position', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'verbose_name': 'Category',
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=80)),
                ('position', models.IntegerField(default=0, verbose_name='Position', blank=True)),
                ('description', models.TextField(default='', verbose_name='Description', blank=True)),
                ('updated', models.DateTimeField(verbose_name='Updated', null=True)),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('css_icon', models.CharField(default='', verbose_name='Css icon', max_length=64, blank=True)),
                ('is_hidden', models.BooleanField(default=False, verbose_name='is hidden')),
                ('is_private', models.BooleanField(default=False, verbose_name='is private')),
                ('category', models.ForeignKey(verbose_name='Category', related_name='forums', to='pybb.Category')),
                ('moderators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Moderators', null=True, blank=True)),
                ('participants', models.ManyToManyField(help_text='private participants list', to=settings.AUTH_USER_MODEL, null=True, related_name='forum_user_sets', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Forums',
                'verbose_name': 'Forum',
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(help_text='poll title', verbose_name='title', max_length=2048)),
                ('voted_amount', models.PositiveIntegerField(default=0, verbose_name='voted amount', help_text='amount of voted user, cache field')),
                ('items_amount', models.PositiveIntegerField(default=2, verbose_name='items amount', help_text='positive amount of poll items for further creation')),
                ('is_multiple', models.BooleanField(default=False, verbose_name='is multiple', help_text='is multiple select allowed')),
                ('is_prepared', models.BooleanField(default=False, verbose_name='is prepared', help_text='marks if poll is prepared to rock n roll')),
                ('is_finished', models.BooleanField(default=False, verbose_name='is finished', help_text='marks if poll is finished')),
                ('date_expire', models.DateTimeField(help_text='date then poll is expired', verbose_name='date expire', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Polls',
                'verbose_name': 'Poll',
            },
        ),
        migrations.CreateModel(
            name='PollAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('poll', models.ForeignKey(to='pybb.Poll', related_name='answer_poll_set')),
            ],
            options={
                'verbose_name_plural': 'Poll answers',
                'verbose_name': 'Poll answer',
            },
        ),
        migrations.CreateModel(
            name='PollItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(verbose_name='title', max_length=2048)),
                ('voted_amount', models.PositiveIntegerField(default=0, verbose_name='voted amount', help_text='amount of voted user, cache field')),
                ('score', models.DecimalField(default=0, verbose_name='score', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], help_text='score in percent', decimal_places=2, max_digits=10)),
                ('poll', models.ForeignKey(to='pybb.Poll', related_name='poll_item_poll_set')),
            ],
            options={
                'verbose_name_plural': 'Poll items',
                'verbose_name': 'Poll item',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Created', blank=True)),
                ('updated', models.DateTimeField(verbose_name='Updated', null=True, blank=True)),
                ('markup', models.CharField(default='textile', verbose_name='Markup', choices=[('textile', 'textile'), ('bbcode', 'bbcode'), ('markdown', 'markdown')], max_length=15)),
                ('body', models.TextField(verbose_name='Message')),
                ('body_html', models.TextField(verbose_name='HTML version')),
                ('body_text', models.TextField(verbose_name='Text version')),
                ('user_ip', models.IPAddressField(default='127.0.0.1', verbose_name='User IP', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Posts',
                'verbose_name': 'Post',
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='Read',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('time', models.DateTimeField(verbose_name='Time', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Topic Reads',
                'verbose_name': 'Topic Read',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Subject', max_length=255)),
                ('created', models.DateTimeField(verbose_name='Created', null=True)),
                ('updated', models.DateTimeField(verbose_name='Updated', null=True)),
                ('views', models.IntegerField(default=0, verbose_name='Views count', blank=True)),
                ('sticky', models.BooleanField(default=False, verbose_name='Sticky')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('forum', models.ForeignKey(verbose_name='Forum', related_name='topics', to='pybb.Forum')),
                ('subscribers', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Subscribers', related_name='subscriptions', blank=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Topics',
                'verbose_name': 'Topic',
                'ordering': ['-created'],
            },
        ),
        migrations.AddField(
            model_name='read',
            name='topic',
            field=models.ForeignKey(verbose_name='Topic', to='pybb.Topic'),
        ),
        migrations.AddField(
            model_name='read',
            name='user',
            field=models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(verbose_name='Topic', related_name='posts', to='pybb.Topic'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(verbose_name='User', related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pollanswer',
            name='poll_item',
            field=models.ForeignKey(to='pybb.PollItem', related_name='answer_poll_item_set'),
        ),
        migrations.AddField(
            model_name='pollanswer',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='answer_user_set'),
        ),
        migrations.AddField(
            model_name='poll',
            name='topic',
            field=models.ForeignKey(to='pybb.Topic', related_name='poll_topic_set', unique=True),
        ),
        migrations.AddField(
            model_name='anonymouspost',
            name='topic',
            field=models.ForeignKey(verbose_name='Topic', to='pybb.Topic', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='read',
            unique_together=set([('user', 'topic')]),
        ),
    ]
