
from django.db import models
from copy import deepcopy

def copy_fields(src, dest):
    for dstfield in src._meta.fields:
        if dstfield.name not in ('pk', 'id'):
            clone = None
            attr_value = getattr(src, dstfield.name)
            clone = deepcopy(attr_value)
            setattr(dest, dstfield.name, clone)


class DynamicChoiceField(models.CharField):

    def _get_choices(self):
        if hasattr(self._choices, 'next'):
            choices, self._choices = tee(self._choices() if callable(self._choices) else self._choices)
            return choices
        else:
            return self._choices() if callable(self._choices) else self._choices
    choices = property(_get_choices)