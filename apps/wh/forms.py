# ^^, coding: utf-8 ^^,
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from cStringIO import StringIO
from PIL import Image
from apps.wh.models import User
from apps.wh.models import Side,RegisterSid, Skin, Army
from apps.core import get_safe_message
from apps.core.forms import RequestModelForm
from django.contrib.auth.models import User
import re
#from apps.core.forms import RequestForm

#requests request variable from views
class RequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
                if 'request' in kwargs:
                        self.request = kwargs['request']
                        del kwargs['request']
                super(RequestForm, self).__init__(*args, **kwargs)
#implement more
class WarningForm(RequestForm):
    from django.conf import settings
    nickname = forms.CharField(widget=forms.HiddenInput())
    level = forms.ChoiceField(choices=settings.SIGN_CHOICES,required=False)
    comment = forms.CharField(required=False,widget=forms.Textarea({'cols':40,'rows':10}))
    next = forms.CharField(required=False,widget=forms.HiddenInput())
    
    def clean_level(self):
        from django.conf import settings
        level = int(self.cleaned_data.get('level',1))
        if level>len(settings.SIGN_CHOICES) or level<=0:
            raise form.ValidationError(_('Level should not be greater than %i' % len(settings.SIGN_CHOICES)))
        return level

class UploadAvatarForm(forms.Form):
    avatar = forms.ImageField()

    def clean_avatar(self):
        value = self.cleaned_data.get('avatar','')
        file = ''
        for i in value.chunks(): file += i
        #content = value.read()
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise form.ValidationError(_('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid avatar. The file you uploaded was either not an image or a corrupted image.'))
        if y>100 or x >100:
            raise forms.ValidationError(_('Upload a valid avatar. Avatar\'s size should not be greater than 100x100 pixels'))
        return value

class UpdateProfileModelForm(RequestModelForm):
    required_css_class='required'
    side = forms.ChoiceField(choices=((i.id, i.name) for i in Side.objects.all()), required=False)
    army = forms.ModelChoiceField(queryset=Army.objects, required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'nickname', 'avatar', 'photo',
            'gender', 'jid', 'uin', 'about', 'skin', 'side', 'army', 'tz'
        ]
        exclude = ['password', 'username', 'groups', 'ranks', 'user_permissions', 'is_staff',
            'is_superuser', 'is_active', 'last_login', 'date_joined', 'plain_avatar',
        ]

    def clean_nickname(self):
        current_nickname = self.request.user.nickname
        value = self.cleaned_data.get('nickname','')
        r = re.compile('[\w\s-]+',re.U)
        if r.match(value):
            return r.match(value).group()
        else:
            raise forms.ValidationError(_('You can not use additional symbols in you nickname'))
        try:
            user = User.objects.get(nickname__exact=value)
            if not user.nickname == current_nickname:
                raise forms.ValidationError(_('Another user with %s nickname exists.' % (value)))
            else:
                return value
        except User.DoesNotExist:
            return value

    def clean_avatar(self):
        value = self.cleaned_data.get('avatar','')
        if not value: return None
        file = ''
        for i in value.chunks(): file += i
        #content = value.read()
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise form.ValidationError(_('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid avatar. The file you uploaded was either not an image or a corrupted image.'))
        if y>100 or x >100:
            raise forms.ValidationError(_('Upload a valid avatar. Avatar\'s size should not be greater than 100x100 pixels'))
        return value

    def clean_photo(self):
        value = self.cleaned_data.get('photo','')
        if not value: return None
        file = ''
        for i in value.chunks(): file += i
        #content = value.read()
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise form.ValidationError(_('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid avatar. The file you uploaded was either not an image or a corrupted image.'))
        return value
    
    def clean_jid(self):
        jid = self.cleaned_data['jid']
        if jid:
            from apps.core.helpers import get_object_or_none
            u = self.request.user
            user = get_object_or_none(User, jid__iexact=jid)
            if user and user != u:
                raise forms.ValidationError(_('User with such JID already exists'))
        return "".join(jid).lower()

#obsolete
class UpdateProfileForm(RequestForm):
    #TODO: make something with None fraction, delete it or not?
    #sides = Side.objects.exclude(fraction__title__iexact='None').order_by('id')
    sides = Side.objects.all().order_by('id').exclude(name__iexact='None')
    skins = Skin.objects.all()
    SIDES_CHOICE, SKIN_CHOICES = list(), list()
    SKIN_CHOICES.append([0,_('-----')])
    n = 0
    for side in sides:
            SIDES_CHOICE.append([side.id,side.name])
            n += 1
            #print side.name
    for skin in skins: SKIN_CHOICES.append([skin.id, skin.name])
    GENDER_FIELD = (
        ('m',_('Male')),
        ('f',_('Female')),
        ('n',_('Not identified')),

    )
    avatar = forms.ImageField(required=False)
    photo = forms.ImageField(required=False)
    nickname = forms.CharField(required=False)
    side =    forms.ChoiceField(choices=SIDES_CHOICE,required=False)
    #army = forms.ChoiceField(choices=((0,_('Choose Side')),), required=False)
    gender = forms.ChoiceField(choices=GENDER_FIELD, required=False)
    jid    = forms.EmailField(required=False)
    uin    = forms.IntegerField(required=False)
    about    = forms.CharField(widget=forms.Textarea(), required=False)
    email   = forms.EmailField(required=False)
    skin    = forms.ChoiceField(choices=SKIN_CHOICES)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    def clean_avatar(self):
        value = self.cleaned_data.get('avatar','')
        if not value: return None
        file = ''
        for i in value.chunks(): file += i
        #content = value.read()
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise form.ValidationError(_('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid avatar. The file you uploaded was either not an image or a corrupted image.'))
        if y>100 or x >100:
            raise forms.ValidationError(_('Upload a valid avatar. Avatar\'s size should not be greater than 100x100 pixels'))
        return value

    def clean_photo(self):
        value = self.cleaned_data.get('photo','')
        if not value: return None
        file = ''
        for i in value.chunks(): file += i
        #content = value.read()
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise form.ValidationError(_('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid avatar. The file you uploaded was either not an image or a corrupted image.'))
        return value
    
    def clean_jid(self):
        jid = self.cleaned_data['jid']
        from apps.core.helpers import get_object_or_none
        u = self.request.user
	user = get_object_or_none(User,jid__iexact=jid)
        if user and user != u:
            raise forms.ValidationError(_('User with such JID already exists'))
        return "".join(jid).lower()
    
    def clean_nickname(self):
        current_nickname = self.request.user.nickname
        value = self.cleaned_data.get('nickname','')
        r = re.compile('[\w\s-]+',re.U)
        if r.match(value):
            return r.match(value).group()
        else:
            raise forms.ValidationError(_('You can not use additional symbols in you nickname'))
        try:
            user = User.objects.get(nickname__exact=value)
            if not user.nickname == current_nickname:
                raise forms.ValidationError(_('Another user with %s nickname exists.' % (value)))
            else:
                return value
        except User.DoesNotExist:
            return value

    def clean_skin(self):
        value = self.cleaned_data.get('skin', '')
        try:
            skin = Skin.objects.get(id=int(value))
            return value
        except Skin.DoesNotExist:
            raise forms.ValidationError(_('There\'s no any mention for this skin, try to update page and upload profile one more time'))
    
    #self limit is on the 512 value, but there is some issues
    def clean_about(self):
        value = self.cleaned_data.get('about','')
        if len(value)> 200:
            raise forms.ValidationError(_('Your about field should not be greater than 200 chars'))
        else:
            return value

class PMForm(RequestForm):
    title = forms.CharField()
    addressee = forms.CharField()
    content = forms.CharField(widget=forms.Textarea())
    #recieving all request :)
    
    #def __init__(self, *args, **kwargs):
    #    if 'request' in kwargs:
    #        self.request = kwargs['request']
    #        del kwargs['request']
    #    super(PMForm, self).__init__(*args, **kwargs)
    
    def clean_content(self):
        message = self.cleaned_data.get('content','')
        message = get_safe_message(message)
        return message

    def clean(self):
        cleaned_data = self.cleaned_data
        sender = self.request.user
        addressee = cleaned_data.get('addressee','')
        try:
            a = User.objects.get(nickname=addressee)
            if sender == a:
                msg = _('You can not send private messages to yourself')
                self._errors['addressee'] = ErrorList([msg])
                del cleaned_data['addressee']
        except User.DoesNotExist:
            msg = _('There\'s no user with such nickname, sorry')
            self._errors['addressee'] = ErrorList([msg])
            del cleaned_data['addressee']
        return cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField()
    nickname = forms.CharField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    answ = forms.CharField()
    sid = forms.CharField(required=False, widget=forms.HiddenInput()) #should be hidden, supports error info for wrong image answer formations
 
    def clean_username(self):
        value = self.cleaned_data.get('username', '')
        try:
            u = User.objects.get(username=value)
            raise forms.ValidationError(_('There\'s already user with such login here'))
        except User.DoesNotExist:
            return value
    def clean_email(self):
        value = self.cleaned_data.get('email', '')
        try:
            u = User.objects.get(email=value)
            raise forms.ValidationError(_('User with such email already exists'))
        except User.DoesNotExist:
            return value
    def clean_nickname(self):
        value = self.cleaned_data.get('nickname', '')
        if not value: return value

        r = re.compile('[\w\s-]+',re.U)
        
        if r.match(value):
            return r.match(value).group()
        else:
            raise forms.ValidationError(_('You can not use additional symbols in you nickname'))
        
        try:
            if_busy = User.objects.get(nickname=value)
            raise forms.ValidationError(_('This nick is busy, sorry'))
        except User.DoesNotExist:
            return value

    def clean(self):
        cleaned_data = self.cleaned_data
        password1 = cleaned_data.get('password1','')
        password2 = cleaned_data.get('password2','')
        sid = cleaned_data.get('sid','')
        answ = cleaned_data.get('answ','')
        if password1 != password2:
            msg = _('Passwords ain\'t matching')
            self._errors['password1'] = ErrorList([msg])
            self._errors['password2'] = ErrorList([msg])
            del cleaned_data['password1']
            del cleaned_data['password2']
        try:
            rsid = RegisterSid.objects.get(sid=sid)
            if rsid.value != answ:
                msg=_('You\'ve type wrong answer')
                self._errors['answ'] = ErrorList([msg])
                if answ: del cleaned_data['answ']
        except RegisterSid.DoesNotExist:
            #it should not happen, besides do nothing
            msg = _('Something went wrong :(, please try again')
            self._errors['answ'] = ErrorList([msg])
            if answ: del cleaned_data['answ']
        return cleaned_data

class RecoverForm(forms.Form):
    email = forms.EmailField()
    
class AddWishForm(forms.Form):
    post = forms.CharField(widget=forms.Textarea())

class PasswordChangeForm(RequestForm):
    old_password = forms.CharField(widget=forms.PasswordInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    #def __init__(self, *args, **kwargs):
    #    if 'request' in kwargs:
    #        self.request = kwargs['request']
    #        del kwargs['request']
    #    super(PasswordChangeForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        old_password = cleaned_data.get('old_password','')
        password1 = cleaned_data.get('password1','')
        password2 = cleaned_data.get('password2','')
        current_user = self.request.user
        if current_user.check_password(old_password):
            if password1 != password2:
                msg =_('Password1 and Password2 does not match')
                self._errors['password1'] = ErrorList([msg])
                if password1: del cleaned_data['password1']
                if password2: del cleaned_data['password2']
                if old_password: del cleaned_data['old_password']
        else:
            msg = _('Your current password does not match with one you\'ve input')
            self._errors['old_password'] = ErrorList([msg])
            if old_password: del cleaned_data['old_password']
            if password1: del cleaned_data['password1']
            if password2: del cleaned_data['password2']
        return cleaned_data

#class PwdRecoverForm(forms.Form):

class PasswordRecoverForm(RequestForm):
        email = forms.EmailField()
        login = forms.CharField()

        #def __init__(self, *args, **kwargs):
        #        if 'request' in kwargs:
        #                self.request = kwargs['request']
        #                del kwargs['request']
        #        super(PasswordRecoverForm, self).__init__(*args, **kwargs)

        def clean(self):
                cleaned_data = self.cleaned_data
                email = self.cleaned_data.get('email','')
                login = self.cleaned_data.get('login','')
                try:
                        u = User.objects.get(username__iexact=login,email__iexact=email)
                except User.DoesNotExist:
                        if login: del cleaned_data['login']
                        if email: del cleaned_data['email']
                        msg = _('No such user with such email')
                        self._errors['login'] = ErrorList([msg])
                return cleaned_data

