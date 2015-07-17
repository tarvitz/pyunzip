# coding: utf-8


def check_fraction(user, voter):
    if 'None' in user.fraction or 'None' in voter.fraction:
        return True
    if user.army.side.fraction == voter.army.side.fraction:
        return True
