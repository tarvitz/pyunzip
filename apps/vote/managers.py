# coding: utf-8
from django.db import models,connection
from django.conf import settings

class BestManager(models.Manager):
    def get_query_set(self):
        super_class = super(BestManager, self)
        return super_class.get_query_set().extra(select={
            'raiting':'(score/votes)'
            },
            where=["votes >= %(vote_amount)s AND score/votes>=%(average)s" %
                {
                    'vote_amount': settings.VOTE_AMOUNT,
                    'average': settings.VOTE_AVERAGE,
                }
            ]
        ).order_by('-score','-votes')

