# coding: utf-8
from apps.menu.models import VMenuItem, HMenuItem
def menu(request):
    return {
        'hmenu': HMenuItem.objects.filter(is_hidden=False),
        'vmenu': VMenuItem.objects.filter(parent=None,
            is_hidden=False),
    }
