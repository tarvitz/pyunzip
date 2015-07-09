# coding: utf-8
from django.core.exceptions import ValidationError
_ = lambda s: s

__all__ = [
    'validate_user_context',
]


def validate_user_context(value):
    if value < 0 or value >= 4:
        raise ValidationError(_("You can not override user context"))
    return value
