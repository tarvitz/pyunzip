# coding: utf-8
from apps.karma.models import Karma
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect


# obsolete, todo: remove
def day_expired(func,):
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        k = Karma.objects.filter(voter=user)
        if k:
            k = k[0]
            now = datetime.now()
            if k.date+timedelta(hours=24) < now:
                return func(*args, **kwargs)
            else:
                return HttpResponseRedirect('/timeout/')
        else:
            return func(*args, **kwargs)
    return wrapper


def amount_expired(func):
    def wrapper(request, *args, **kwargs):
        offset = datetime.now() - timedelta(
            minutes=settings.KARMA_TIMEOUT_MINUTES)
        karmas = request.user.karma_voter_set.filter(date__gte=offset)
        if (karmas.count() >= settings.KARMA_PER_TIMEOUT_AMOUNT
                and not request.user.has_perm('karma.change_karma')):
            return redirect('core:timeout')
        return func(request, *args, **kwargs)
    return wrapper
