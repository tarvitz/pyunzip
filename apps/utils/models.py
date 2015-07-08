# -*- coding: utf-8 -*-

from copy import deepcopy

def copy_fields(src, dest):
    for dstfield in src._meta.fields:
        if dstfield.name not in ('pk', 'id'):
            clone = None
            attr_value = getattr(src, dstfield.name)
            clone = deepcopy(attr_value)
            setattr(dest, dstfield.name, clone)
