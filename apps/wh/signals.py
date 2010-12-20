from django.db.models.signals import pre_save,post_save
from apps.wh.actions import rank_scheme_alter
from django.contrib.auth.models import User

def user_saved(instance, **kwargs):
    #print "user_saved function is active"
    rank_scheme_alter(instance,**kwargs)

def setup_signals():
    pre_save.connect(rank_scheme_alter,sender=User)

