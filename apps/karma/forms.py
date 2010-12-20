from django import forms
from django.utils.translation import ugettext_lazy as _

class AlterKarmaForm(forms.Form):
    #choice = forms.ChoiceField(widget=forms.RadioSelect(),choices=((-1,'+1'),(1,'-1')))
    comment = forms.CharField(widget=forms.Textarea())
    hidden_nickname = forms.CharField(widget=forms.HiddenInput())
    referer = forms.CharField(widget=forms.HiddenInput())
    url =   forms.CharField(widget=forms.HiddenInput(),required=False)
