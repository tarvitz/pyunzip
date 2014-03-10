from apps.accounts.models import User
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
import django_filters
from django import forms
from apps.core.widgets import DateTimePickerInput

CHOICES = (
    ('', _("Any")),
    (True, pgettext_lazy("is active on select", "Active")),
    (False, pgettext_lazy("is inactive on select", "Inactive"))
)

class RoleFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': _("Email"),
            'data-title': _("User email"), 'rel': 'tooltip',
            'data-delay': 300
        }),
        lookup_type='icontains'
    )
    is_operator = django_filters.BooleanFilter(
        label=_('operator'),
        widget=forms.Select(
            attrs={
                'rel': 'tooltip', 'data-delay': 300,
                'data-title': _("Operator")
            },
            choices=CHOICES
        )
    )
    is_teacher = django_filters.BooleanFilter(
        label=_("teacher"),
        widget=forms.Select(
            attrs={
                'rel': 'tooltip', 'data-delay': 300,
                'data-title': _("Teacher")
            }, choices=CHOICES
        )
    )

    class Meta:
        model = User
        fields = [
            'is_operator', 'is_teacher', 'email',
        ]