# coding: utf-8
from apps.core import get_safe_message
from apps.core.helpers import get_object_or_none
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from apps.core.forms import RequestForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget
#from apps.wh.models import Side
from django.forms.util import ErrorList
#from apps.tabletop.models import Mission,Roster
import re

class VoteForm(RequestForm):
    comment = forms.CharField(widget=forms.Textarea(),required=False)
    next = forms.CharField(widget=forms.HiddenInput())
    #value = forms.CharField(widget=forms.HiddenInput())
    
    def clean_value(self):
        value = self.cleaned_data['value']
        if value>5 or value<1:
            raise forms.ValidationError(_('You can not pass value greater than \'5\' or lesser than \'1\''))
