
from django import forms

class DynamicChoiceField(forms.ChoiceField):

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):

        if callable(value):
            value = value()

        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)