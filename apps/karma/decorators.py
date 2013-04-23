#decorators are here
# coding: utf-8
from apps.karma.models import Karma
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponseRedirect

#implement more clear and wise functional of expired fncs
def day_expired(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        request = args[0]
        user = request.user
        k = Karma.objects.filter(voter=user)
        if k:
            k = k[0]
            now = datetime.now()
            if k.date+timedelta(hours=24) < now:
                return func(*args,**kwargs)
            else:
                return HttpResponseRedirect('/timeout')
        else:
            return func(*args,**kwargs)
    return wrapper

def amount_comments_required(amount):
    def decorator(func):
        def wrapper(*args,**kwargs):
            request = args[0]
            count = request.user.get_comments_count()
            if count >= amount:
                return func(*args,**kwargs)
            else:
                return HttpResponseRedirect('/user/power/insufficient/')
        return wrapper
    return decorator

def twenty_comments_required(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        request = args[0]
        if request.user.get_comments_count() > 20:
            return func(*args,**kwargs)
        else:
            return HttpResponseRedirect('/user/power/insufficient/')
    return wrapper
