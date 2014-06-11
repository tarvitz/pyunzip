# coding: utf-8
from django.http import Http404
from django.conf import settings


def prevent_bruteforce(func):
    def wrapper(request, *args, **kwargs):
        if request.session.get(
            'brute_force_iter', 0
        ) > settings.BRUTEFORCE_ITER:
            # should login bastards
            raise Http404(":D fuck you!")
        return func(request, *args, **kwargs)
    return wrapper
