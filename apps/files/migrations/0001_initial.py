# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import apps.files.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('attachment', models.FileField(verbose_name='Attachment', upload_to='/home/lilfox/www/warmist/app/../db/uploads/attachments/')),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('type', models.CharField(verbose_name='Type', choices=[('tech', 'technical'), ('global', 'global'), ('user', 'user')], max_length=30)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Galleries',
                'verbose_name': 'Gallery',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(verbose_name='Title', max_length=100)),
                ('alias', models.CharField(help_text='Fast name to access unit', validators=[apps.files.models.valid_alias], null=True, verbose_name='Alias', blank=True, unique=True, max_length=32)),
                ('comments', models.TextField(verbose_name='Comments')),
                ('image', models.ImageField(verbose_name='Image', upload_to=apps.files.models.Image.upload_to)),
                ('gallery', models.ForeignKey(verbose_name='gallery', to='files.Gallery')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Images',
                'verbose_name': 'Image',
                'ordering': ['-id'],
                'permissions': (('can_upload', 'Can upload images'), ('delete_images', 'Can delete images')),
            },
        ),
        migrations.CreateModel(
            name='UserFile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(null=True, verbose_name='title', blank=True, max_length=256)),
                ('file', models.FileField(verbose_name='file', upload_to=apps.files.models.UserFile.file_upload_to)),
                ('plain_type', models.CharField(help_text='plain type for ', null=True, verbose_name='plain type', blank=True, default='octet/stream', max_length=256)),
                ('size', models.PositiveIntegerField(help_text='file size', default=0, verbose_name='size')),
                ('owner', models.ForeignKey(related_name='user_file_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User files',
                'verbose_name': 'User file',
            },
        ),
    ]
