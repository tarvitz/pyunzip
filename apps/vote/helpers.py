#!/usr/bin/env python
# coding: utf-8
def vote_stars_calculate(vote):
    from math import trunc
    if vote == 0: vote = 0.1
    full = trunc(vote)
    half = vote-full
    if half == 0:
        half = 0.1 #it's a cheat ;)
 #   print "full: %0.2f; half: %0.2f;" % (full,half)
 #   print round(half,1)
    stars = list()
    for i in range(0,full): stars.append('f')
    if full<5:
        # 0.9,0.8 ~= 1
        # 0.6,0,7 ~= 0.5
        # 0.3,0,4 ~= 0.5
        # 0.1,0,2 ~= 0
        if round(half,1) in [0.8,0.9]:
            half = "f"
            pass
        elif round(half,1) in [0.3, 0.4, 0.5, 0.6, 0.7]:
            half = 'h'
        elif round(half,1) in [0.1,0.2]:
            half = 'z'
        stars.append(half)
    #else: 
    #    for i in xrange(0,full): stars.append("f")
    while len(stars)<5:
        stars.append('z')
    return stars
#__name__ - is object which is show what module uses this module :)
if __name__ in "__main__":
    map = [4.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    for m in map:
        print "m: %0.2f, %r"  % (m,vote_stars_calculate(m))

