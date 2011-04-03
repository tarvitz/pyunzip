# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from settings_path import rel_path
from django.conf import settings
import os
#upload schema
UPLOAD_SETTINGS = {
    'default': rel_path('media/files'),
    'files.image': {
        'form':'apps.files.forms.UploadImageForm',
        'helper': 'apps.files.helpers.upload_image',
        'schema': 'images/galleries/',

    },
    'files.file': {
        'form': 'apps.files.forms.FileUploadForm',
        'helper': 'apps.files.helpers.upload_file',
        'schema': 'files/',
    },
    'files.replay':{
        'form': 'apps.files.forms.UploadReplayForm',
        'helper': 'apps.files.helpers.upload_replay',
        'schema': 'replays/',
    }
}
#user settings
SETTINGS = {
    #field              defaults
    'objects_on_page':40,
    'comments_on_page': 30,
    'replays_on_page': 20,
    'news_on_page': 30,
    'pms_on_page': 50,
    'karmas_on_page': 50,
    'rosters_on_page': 30,
    'rates_on_page': 100,
    'hide_jid': False,
    'hide_uin': True, #it's secure by default to hide it to prevent hackers spaming
    'hide_email': True, #the same
    'show_null_karma': True,
    'show_self_null_karma': True,
    'karma_humor': True,
    'invisible': False,
    'auto_update_subscription': False,
    'show_last_news': True,
    'show_last_replays': True,
    'show_quotes': True,
    'show_online_users': True,
    'show_deleted_rosters': False,
    'last_replays_amount':5,
    'last_news_amount': 5,
    'show_karma_block': True,
    'enable_autocomplete': True,
    'enable_dbcss': False,
    #'show_hidden_content': True,
    #'some_field': 10,
    #nonwh
    'show_l4d2_stats': False,
}
#Overriding defaults for AnonymousUser
ANONYMOUS_SETTINGS = {
    'show_online_users': False,
}
#Settings SemiAutoForm
SETTINGS_FIELDS = {
    'objects_on_page': forms.IntegerField(label=_('The Objects on page'),required=True),
    'comments_on_page': forms.IntegerField(label=_('Comments on page'),required=True),
    'replays_on_page': forms.IntegerField(label=_('Replays on page'),required=True),
    'rosters_on_page': forms.IntegerField(label=_('Rosters on page'),required=True),
    'news_on_page': forms.IntegerField(label=_('News on page'),required=True),
    'pms_on_page': forms.IntegerField(label=_('Private messages on page'),required=True),
    'karmas_on_page': forms.IntegerField(label=_('Karma objects on page'),required=True),
    'rates_on_page': forms.IntegerField(label=_('Rates objects on page'),required=True),
    'hide_jid': forms.BooleanField(label=_('Hide JID from viewing by another users'),required=False),
    'hide_email':forms.BooleanField(label=_('Hide Email from viewing by another users'),required=False),
    'hide_uin': forms.BooleanField(label=_('Hide UIN from viewing by another users'),required=False),
    'show_null_karma': forms.BooleanField(label=_('Show karma values which equal to zero'),required=False),
    'show_self_null_karma': forms.BooleanField(label=_('Show karma values which equal to zero only for your karma list'),required=False),
    'karma_humor': forms.BooleanField(label=_('Show humor status for users karma highness'),required=False),
    'invisible': forms.BooleanField(label=_('If you do not want to show your precense on the site check this on'),required=False),
    'auto_update_subscription': forms.BooleanField(label=_('Auto updates your subscription if you are reading the comments or object you have been subscribed'),required=False),
    'show_last_news': forms.BooleanField(label=_('Show Last News block'),required=False),
    'show_last_replays': forms.BooleanField(label=_('Show Last Replays block'),required=False),
    'show_quotes': forms.BooleanField(label=_('Show Quotes block'),required=False),
    'show_online_users': forms.BooleanField(label=_('Show Online Users block'),required=False),
    'show_deleted_rosters': forms.BooleanField(label=_('Show deleted rosters'),required=False),
    'last_replays_amount': forms.IntegerField(label=_('Last Replays block objects amount')),
    'last_news_amount': forms.IntegerField(label=_('Last News block objects amount')),
    'show_karma_block': forms.BooleanField(label=_('Show karma block'),required=False),
    'enable_autocomplete': forms.BooleanField(label=_('Enables autocomplete on site'),required=False),
    'enable_dbcss': forms.BooleanField(label=_('Enables user css styles hosted in database'),required=False),
   #'show_hidden_content': forms.BooleanField(label=_('show hidden stuff'),required=False),
    #nonwh
    'show_l4d2_stats': forms.BooleanField(label=_('Show L4D stats block'),required=False),
    #'some_field': forms.IntegerField(label=_('Some field'),required=False),

}

class SettingsFormOverload(object):
    """does not work ... why?"""
    """
    #make below as verification under clean()
    def clean(self):
        cleaned_data = self.cleaned_data
        map = ['objects_on_page','comments_on_page','replays_on_page','news_on_page','pms_on_page','karmas_on_page']
        for m in map:
            value = cleaned_data.get(m)
            if value<10:
                msg = _('Value you\'ve passed must be greater than 10')
                self._errors[m] = ErrorList([msg])
                del cleaned_data[m]
        return cleaned_data
    """
    def clean_last_news_amount(self):
        lna = self.cleaned_data.get('last_news_amount',None)
        if lna>=5 and lna<=15:
            return self.cleaned_data['last_news_amount']
        else:
            raise forms.ValidationError(_('You can not pass number lesser than 5 and greater than 15'))
    def clean_last_replays_amount(self):
        lra = self.cleaned_data.get('last_replays_amount',None)
        if lra>=5 and lra<=15:
            return lra
        else:
            raise forms.ValidationError(_('You can not pass number lesser than 5 and greater than 15'))

    def clean_objects_on_page(self):
        if self.cleaned_data['objects_on_page'] < 10:
            raise forms.ValidationError(_("You can not pass number lesser than 10"))
        return self.cleaned_data['objects_on_page'] 
    def clean_comments_on_page(self):
        if self.cleaned_data['comments_on_page'] <10:
            raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['comments_on_page']
    def clean_replays_on_page(self):
        if self.cleaned_data['replays_on_page'] <10:
           raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['replays_on_page']
    def clean_news_on_page(self):
        if self.cleaned_data['news_on_page'] < 10:
            raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['news_on_page']
    def clean_pms_on_page(self):
        if self.cleaned_data['pms_on_page'] < 10:
            raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['pms_on_page']
    def clean_karmas_on_page(self):
        if self.cleaned_data['karmas_on_page'] < 10:
            raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['karmas_on_page']
    def clean_rosters_on_page(self):
        if self.cleaned_data['rosters_on_page'] < 10:
            raise forms.ValidationError(_('You can not pass number lesser than 10'))
        return self.cleaned_data['rosters_on_page']
    
    def clean_rates_on_page(self):
        if self.cleaned_data['rates_on_page'] < 40:
            raise forms.ValidationError(_('You can not pass number lesser than 40'))
        return self.cleaned_data['rates_on_page']
    

SECURE_SETTINGS = {
    r'display_online_users': '',
    r'display_menu_quotes': '',
    r'display_last_replays': '',
    r'display_briefing_news': '',

}
