# coding: utf-8
from django import forms


class EventPlaceForm(forms.ModelForm):
    class Meta:
        widgets = {
            'contacts': forms.Textarea,
            'address': forms.Textarea
        }