
from apps.quotes.models import QueueQuote
from django import forms

class QueueQuoteForm(forms.ModelForm):

    text = forms.CharField(widget=forms.Textarea())
    
    def clean_text(self):
        return self.cleaned_data.get('text', '')[:4096]

    class Meta:
        model = QueueQuote
        fields = ('text',)