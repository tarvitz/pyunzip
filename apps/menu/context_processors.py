# coding: utf-8
from apps.menu.models import VMenuItem, HMenuItem
from django.core.cache import cache


def menu(request):
    hmenu = cache.get('hmenu:all')
    if not hmenu:
        hmenu = HMenuItem.objects.filter(
            is_hidden=False
        )
        cache.set('hmenu:all', hmenu)
    vmenu = cache.get('vmenu:top')
    if not vmenu:
        VMenuItem.objects.filter(
            parent=None,
            is_hidden=False
        )
        cache.set('vmenu:all', vmenu)
    return {
        'hmenu': hmenu,
        'vmenu': vmenu
    }
