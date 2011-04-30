# coding: utf-8
from django import forms

class NonCheckChoiceField(forms.ChoiceField):
    widget = forms.widgets.Select
    def __init__(self, choices=(), required=True, widget=None,
        label=None, initial=None, help_text=None, *args, **kwargs):
            super(NonCheckChoiceField, self).__init__(*args, **kwargs)

    def validate(self, value):
        pass

    def valid_value(self, value):
        return value

class NonCheckMultipleChoiceField(forms.MultipleChoiceField):
    widget = forms.widgets.SelectMultiple
    def __init__(self, choices=(), required=True, widget=None,
        label=None, initial=None, help_text=None, *args, **kwargs):
            super(NonCheckMultipleChoiceField, self).__init__(choices, required,
                widget, label, initial, help_text,*args, **kwargs)

    def validate(self, value):
        pass

    def valid_value(self, value):
        return value

