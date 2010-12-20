# coding: utf-8
from apps.wh.models import Rank
from apps.core.helpers import get_object_or_none
from django.db.models import Q

#TODO: FIXME:works INCORRECT,overwrite
def rank_scheme_alter(instance,**kwargs):
    if instance.pk:
    	ranks = instance.ranks.distinct().order_by('type__magnitude')
    	if not ranks:
        	first_rank = get_object_or_none(Rank,codename='users')
		if first_rank:
			instance.ranks.add(Rank.objects.get(codename='users'))
    	#alter user if he or she could be staff or not
    	if not instance.is_staff and instance.get_magnitude()<= 100:
        	instance.is_staff = True
    	if instance.is_staff and instance.get_magnitude() > 100:
        	instance.is_staff = False
    return instance
