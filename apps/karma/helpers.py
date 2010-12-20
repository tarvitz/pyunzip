# coding: utf-8
#

def check_fraction(user,voter):
    #none fraction could alter karma of everybody
    #the same way everybody could alter karma of None fractioned users
    if 'None' in user.fraction or 'None' in voter.fraction: return True
    if user.army.side.fraction == voter.army.side.fraction: return True
