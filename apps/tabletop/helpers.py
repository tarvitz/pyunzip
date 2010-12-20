# coding: utf-8
from django.db.models import Q
def process_roster_query(roster_query):
    """ returns formatted query set """
    qset = Q()
    kw = dict()
    if roster_query['player']:
        qset_nicks = (
            Q(owner__nickname__icontains=roster_query['player'])|
            Q(user__nickname__icontains=roster_query['player'])|
            Q(player__icontains=roster_query['player'])
        )
    else:
        qset_nicks = Q()

    if roster_query['pts']:
        sign = roster_query['pts_sign']
        if sign == '>': kw.update({'pts__gt': roster_query['pts']})
        elif sign == '<': kw.update({'pts__lt': roster_query['pts']})
        elif sign == '<=': kw.update({'pts__lte': roster_query['pts']})
        elif sign == '>=': kw.update({'pts__gte': roster_query['pts']})
        else: kw.update({'pts':roster_query['pts']})
    #race__name__icontains=u'' makes some mistakes within rosters retrieving if there is nothing
    #with race field
    if roster_query['race']:
        qset_race = (
            Q(race__name__icontains=roster_query['race'])|
            Q(custom_race__icontains=roster_query['race'])
        )
    else:
        qset_race = Q()
    qset = (
        Q(title__icontains=roster_query['title'],**kw),
        qset_race,
        qset_nicks
    )
    return qset
