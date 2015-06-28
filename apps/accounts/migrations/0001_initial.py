# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
from django.conf import settings
import django.contrib.auth.models
import datetime
import picklefield.fields
import django.utils.timezone
import django.core.validators
import apps.accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('wh', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PM',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='title')),
                ('content', models.TextField(verbose_name='text')),
                ('cache_content', models.TextField(null=True, blank=True, verbose_name='cache content')),
                ('is_read', models.BooleanField(default=False, verbose_name='is read')),
                ('sent', models.DateTimeField(default=datetime.datetime.now, verbose_name='sent')),
                ('dbs', models.BooleanField(default=False, verbose_name='deleted by sendr')),
                ('dba', models.BooleanField(default=False, verbose_name='deleted by addr')),
                ('syntax', models.CharField(default='textile', null=True, blank=True, max_length=50, verbose_name='syntax', choices=[('textile', 'textile'), ('bb-code', 'bb-code')])),
            ],
            options={
                'verbose_name_plural': 'Private Messages',
                'verbose_name': 'Private Message',
                'ordering': ['-sent'],
            },
        ),
        migrations.CreateModel(
            name='PolicyWarning',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('comment', models.CharField(max_length=4096, null=True, blank=True, verbose_name='comment')),
                ('level', models.PositiveIntegerField(default=1, verbose_name='level', choices=[(1, '*'), (2, '**'), (3, '+'), (4, '++'), (40000, 'read only')])),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, verbose_name='created on')),
                ('updated_on', models.DateTimeField(default=datetime.datetime.now, verbose_name='updated on')),
                ('date_expired', models.DateField(default=datetime.datetime.now, verbose_name='date expired', help_text='date then warning is expired')),
                ('is_expired', models.BooleanField(default=False, help_text='marks if warning is expired for this user', verbose_name='is expired')),
            ],
            options={
                'verbose_name_plural': 'Policy warnings',
                'verbose_name': 'Policy warning',
                'ordering': ['-date_expired'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('username', models.CharField(max_length=40, unique=True, verbose_name='username', validators=[django.core.validators.RegexValidator(re.compile('^[\\w.@+-]+$', 32), 'Enter a valid username.', 'invalid')], help_text='Required. 38 characters or fewer. Letters, numbers and @/./+/-/_ characters')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('nickname', models.CharField(max_length=32, unique=True, blank=True, verbose_name='nickname')),
                ('avatar', models.ImageField(null=True, blank=True, upload_to=apps.accounts.models.User.avatar_upload_to, verbose_name='Avatar')),
                ('plain_avatar', models.ImageField(blank=True, upload_to='/home/lilfox/www/warmist/app/../db/uploadsavatars/', verbose_name='plain Avatar')),
                ('photo', models.ImageField(blank=True, upload_to='/home/lilfox/www/warmist/app/../db/uploadsphotos/', verbose_name='photo')),
                ('gender', models.CharField(default='n', max_length=1, verbose_name='gender', choices=[('m', 'male'), ('f', 'female'), ('n', 'not identified')])),
                ('jid', models.EmailField(max_length=255, null=True, blank=True, verbose_name='jabber id')),
                ('uin', models.IntegerField(default=0, max_length=12, blank=True, null=True, verbose_name='uin (icq number)')),
                ('about', models.CharField(max_length=512, null=True, blank=True, verbose_name='about myself')),
                ('tz', models.FloatField(default=0.0, verbose_name='time zone', choices=[(-12.0, '-12'), (-11.0, '-11'), (-10.0, '-10'), (-9.5, '-09.5'), (-9.0, '-09'), (-8.5, '-08.5'), (-8.0, '-08 PST'), (-7.0, '-07 MST'), (-6.0, '-06 CST'), (-5.0, '-05 EST'), (-4.0, '-04 AST'), (-3.5, '-03.5'), (-3.0, '-03 ADT'), (-2.0, '-02'), (-1.0, '-01'), (0.0, '00 GMT'), (1.0, '+01 CET'), (2.0, '+02'), (3.0, '+03'), (3.5, '+03.5'), (4.0, '+04'), (4.5, '+04.5'), (5.0, '+05'), (5.5, '+05.5'), (6.0, '+06'), (6.5, '+06.5'), (7.0, '+07'), (8.0, '+08'), (9.0, '+09'), (9.5, '+09.5'), (10.0, '+10'), (10.5, '+10.5'), (11.0, '+11'), (11.5, '+11.5'), (12.0, '+12'), (13.0, '+13'), (14.0, '+14')])),
                ('settings', picklefield.fields.PickledObjectField(null=True, blank=True, editable=False, verbose_name='Settings')),
                ('karma', models.IntegerField(default=0, null=True, blank=True, help_text="user's karma", verbose_name='karma')),
                ('birthday', models.DateField(null=True, blank=True, verbose_name='birthday')),
                ('army', models.ForeignKey(null=True, blank=True, verbose_name='army', to='wh.Army')),
                ('groups', models.ManyToManyField(related_name='user_group_set', blank=True, related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', to='auth.Group')),
                ('ranks', models.ManyToManyField(null=True, blank=True, to='wh.Rank')),
                ('user_permissions', models.ManyToManyField(related_name='user_permission_set', blank=True, related_query_name='user', help_text='Specific permissions for this user.', verbose_name='user permissions', to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Users',
                'verbose_name': 'User',
                'ordering': ['date_joined'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='policywarning',
            name='user',
            field=models.ForeignKey(related_name='warning_user_set', verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pm',
            name='addressee',
            field=models.ForeignKey(related_name='addressee', verbose_name='addressee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pm',
            name='sender',
            field=models.ForeignKey(related_name='sender', verbose_name='sender', to=settings.AUTH_USER_MODEL),
        ),
    ]
