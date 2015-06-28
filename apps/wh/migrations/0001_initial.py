# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Army',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=100, verbose_name='army')),
            ],
            options={
                'verbose_name_plural': 'Armies',
                'ordering': ['side'],
                'verbose_name': 'Army',
            },
        ),
        migrations.CreateModel(
            name='Expression',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('author', models.CharField(max_length=100, blank=True, verbose_name='author')),
                ('original_content', models.TextField(help_text='Original text of expression', max_length=500, blank=True, verbose_name='original')),
                ('content', models.TextField(help_text='translation of original sentence', max_length=500, blank=True, verbose_name='translation')),
            ],
            options={
                'verbose_name_plural': 'expressions',
                'ordering': ['id'],
                'verbose_name': 'expression',
            },
        ),
        migrations.CreateModel(
            name='Fraction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=30, verbose_name='fraction')),
            ],
        ),
        migrations.CreateModel(
            name='MiniQuote',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('content', models.CharField(max_length=255, verbose_name='content')),
            ],
            options={
                'verbose_name_plural': 'Mini Quotes',
                'verbose_name': 'Mini Quote',
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('short_name', models.CharField(max_length=50, verbose_name='short name')),
                ('codename', models.CharField(max_length=100, unique=True, verbose_name='codename')),
                ('description', models.TextField(verbose_name='description')),
                ('magnitude', models.IntegerField(help_text='Lower magnitude more powerfull', null=True, blank=True, verbose_name='magnitude')),
                ('is_general', models.BooleanField(verbose_name='is General', default=False)),
                ('syntax', models.CharField(null=True, max_length=50, blank=True, choices=[('textile', 'textile'), ('bb-code', 'bb-code')], verbose_name='syntax')),
            ],
            options={
                'verbose_name_plural': 'Ranks',
                'verbose_name': 'Rank',
            },
        ),
        migrations.CreateModel(
            name='RankType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('magnitude', models.IntegerField(help_text='lower magnitude id more powerfull', verbose_name='magnitude')),
                ('style', models.TextField(max_length=1024, blank=True, null=True, verbose_name='CSS Style')),
                ('css_class', models.CharField(max_length=64, blank=True, null=True, verbose_name='CSS class')),
                ('css_id', models.CharField(max_length=64, blank=True, null=True, verbose_name='CSS id')),
                ('group', models.ForeignKey(null=True, to='auth.Group', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Side',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=40, verbose_name='side')),
                ('fraction', models.ForeignKey(to='wh.Fraction')),
            ],
        ),
        migrations.CreateModel(
            name='Universe',
            fields=[
                ('codename', models.CharField(unique=True, max_length=100, serialize=False, verbose_name='сodename', primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
            ],
        ),
        migrations.AddField(
            model_name='rank',
            name='side',
            field=models.ManyToManyField(to='wh.Side', blank=True),
        ),
        migrations.AddField(
            model_name='rank',
            name='type',
            field=models.ForeignKey(null=True, to='wh.RankType', blank=True),
        ),
        migrations.AddField(
            model_name='fraction',
            name='universe',
            field=models.ForeignKey(null=True, to='wh.Universe', blank=True),
        ),
        migrations.AddField(
            model_name='expression',
            name='fraction',
            field=models.ForeignKey(to='wh.Fraction'),
        ),
        migrations.AddField(
            model_name='army',
            name='side',
            field=models.ForeignKey(to='wh.Side'),
        ),
    ]
