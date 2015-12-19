# -*- coding: utf-8 -*-
"""
.. module:: apps.pybb.management.commands.update_index
    :synopsis: Update post ranking index
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from apps.pybb.models import Topic
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Build index topic posts ranking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic-id', dest='topic_id', nargs='+', type=int, default=None
        )

    def handle(self, *args, **options):
        topics_ids = options.get('topic_id', [])
        if topics_ids:
            topics = Topic.objects.filter(pk__in=topics_ids)
        else:
            topics = Topic.objects.all()
        count = topics.count()

        for topic in topics:
            topic.build_post_index()
        self.stdout.write(
            self.style.SUCCESS('Successfully updated %i of topics' % count)
        )
