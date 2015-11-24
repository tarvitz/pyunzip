# -*- coding: utf-8 -*-
from django.utils import timezone

from haystack import indexes
from . import models


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return models.Post

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated__lte=timezone.now())


class TopicIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return models.Topic

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated__lte=timezone.now())
