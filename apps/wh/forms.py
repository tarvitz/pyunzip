# ^^, coding: utf-8 ^^,
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from cStringIO import StringIO
from PIL import Image
from apps.wh.models import User
from apps.wh.models import Side,RegisterSid, Skin, Army, PM
from apps.core import get_safe_message
from apps.core.helpers import get_object_or_None
from apps.core.models import UserSID
from apps.core.forms import RequestModelForm, BruteForceCheck
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib import auth
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

class PMForm(RequestModelForm):
    addressee = forms.ModelChoiceField(
        label=_("Addressee"),
        widget=forms.Select(attrs={
            'class': 'ajax-chosen',
            'url': reverse('json:wh:users')
        }),
        queryset=User.objects.none()
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'markitup'})
    )

    def __init__(self, *args, **kwargs):
        super(PMForm, self).__init__(*args, **kwargs)
        if all(self.data or [None, ]):
            self.base_fields['addressee'].queryset = User.objects
            self.fields['addressee'].queryset = User.objects
        else:
            self.base_fields['addressee'].queryset = User.objects.none()
            self.fields['addressee'].queryset = User.objects.none()

    def clean(self):
        cleaned_data = self.cleaned_data
        sender = self.request.user
        addressee = cleaned_data.get('addressee','')
        try:
            a = User.objects.get(nickname=addressee)
            if sender == a:
                msg = _('You can not send private messages to yourself')
                self._errors['addressee'] = ErrorList([msg])
        except User.DoesNotExist:
            msg = _('There\'s no user with such nickname, sorry')
            self._errors['addressee'] = ErrorList([msg])
        return cleaned_data

    def save(self, commit=True):
        self.instance.sender = self.request.user
        self.instance.addressee = self.cleaned_data['addressee']
        return super(PMForm, self).save(commit)

    class Meta:
        model = PM
        fields = ('addressee', 'title', 'content')

class RegisterForm(forms.Form):
    username = forms.RegexField(
        label=_("Username"),
        regex=re.compile(r'^[A-z][\w\d\._-]+\w+$'),
        max_length=32,
        min_length=3,
        error_message=_('Try to pass only latin symbols, numbers and underscores with your nickname'),
        help_text=_('Only latin symbols and numbers and underscore are allowed'),

    )
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


class SuperUserLoginForm(forms.ModelForm):
    username = forms.CharField(label=_('username'))
    class Meta:
        model = User
        fields = []


class LoginForm(forms.ModelForm):
    #username = forms.CharField(
    #    label=_('username'), required=True
    #)
    password = forms.CharField(
        label=_('password'), widget=forms.PasswordInput(),
        required=True
    )
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if all((username, password)):
            user = auth.authenticate(username=username, password=password)
            if not user:
                msg = _("No user or password match")
                self._errors['username'] = ErrorList([msg])
            else:
                self.cleaned_data['user'] = user
                if not user.is_active:
                    msg = _("You have been banned ;)")
                    self._errors['username'] = ErrorList([msg])
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']


class PasswordRestoreInitiateForm(forms.Form):
    email = forms.CharField(
        label=_("Email"), help_text=_("Your email")
    )

    def clean_email(self):
        email = self.cleaned_data['email'] or None
        users = User.objects.filter(email__iexact=email)
        if not users:
            raise forms.ValidationError(
                _("Users with given email does not exists")
            )
        self.cleaned_data['users'] = users
        return email


class PasswordRestoreForm(RequestModelForm, BruteForceCheck):
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label=_("Password repeat"), widget=forms.PasswordInput()
    )

    def clean(self):
        cd = self.cleaned_data
        password = cd['password']
        password2 = cd['password2']
        if all((password, password2) or (None, )):
            if password != password2:
                msg = _("Passwords don't match")
        return cd

    def save(self, commit=True):
        user = self.instance.user
        user.set_password(self.cleaned_data['password'])
        user.save()
        if commit:
            self.instance.expired = True
            self.instance.save()
            instance = self.instance
        else:
            instance.expired = True
            instance = super(Password, self).save(commit=commit)

        return instance

    class Meta:
        model = UserSID
        exclude = ('expired_date', 'expired', 'sid', 'user')

"""
class PasswordChangeForm(forms.ModelForm):
    old_password = forms.CharField(
        label=_("Old password"), widget=forms.PasswordInput()
    )
    new_password = forms.CharField(
        label=_("New password"), widget=forms.PasswordInput()
    )
    new_password_repeat = forms.CharField(
        label=_("New password repeat"), widget=forms.PasswordInput()
    )

    def clean(self):
        cd = self.cleaned_data
        old_password = cd['old_password']
        new_pwd = cd['new_password']
        new_pwd_repeat = cd['new_password_repeat']
        user = auth.authenticate(
            username=self.instance.username, password=old_password
        )
        if not user:
            msg = _("Old password does not match")
            self._errors['password'] = ErrorMsg([msg])
            if 'password' in cd:
                del cd['password']
        if all((new_pwd, new_pwd_repeat) or (None, )):
            if new_pwd != new_pwd_repeat:
                msg = _("Passwords don't match")
                self._errors['new_password'] = ErrorList([msg])
                if 'new_password' in cd:
                    del cd['new_password']
        return cd

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['new_password'])
        self.instance.save()
        super(PasswordChangeForm, self).save(commit)


    class Meta:
        model = User
        fields = []
"""
