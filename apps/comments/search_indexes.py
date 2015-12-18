# -*- coding: utf-8 -*-
from django.utils import timezone

from haystack import indexes
from . import models


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return models.Comment

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(submit_date__lte=timezone.now())
