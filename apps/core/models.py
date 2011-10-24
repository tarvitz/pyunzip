# coding: utf-8
# try to implement your code 'ere

from django.db import models
from django.utils.translation import ugettext_lazy as _
import cPickle as pickle
from django.contrib.auth.models import User
import base64
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.conf import settings
from apps.core.actions import common_delete_action

"""
class SettingsManager(models.Manager):
    def encode(self, data_dict):
        ###
        ###    Returns the given dictionary pickled as string
        ###
        pickled = pickle.dumps(data_dict)
        return base64.encodestring(pickled)
    
    def save(self,user,data):
        s = self.model(user,self.encode(data))
        if data:
            s.save()
        return s   
    
"""
class Css(models.Model):
    user = models.ForeignKey(User,primary_key=True)
    css = models.TextField(_('CSS'),help_text=_('Cascade Style Sheets'))
    class Meta:
        verbose_name = _('CSS')
        verbose_name_plural = _("CSSes")

class Announcement(models.Model):
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('content type'),
        related_name=_('content_type_set_for_%(class)s'))
    object_pk = models.TextField(_('object id'))
    content_object = generic.GenericForeignKey(ct_field='content type',fk_field='object_pk')
    users = models.ManyToManyField(User,related_name='users',blank=True)
    notified_users = models.ManyToManyField(User,related_name='notified_users',blank=True)
    actions = [common_delete_action, ] 
    #what else ?
    #subscribe the user to get notifications
    def subscribe(self,user):
        if user in self.notified_users.distinct():
            self.users.add(user)
            self.notified_users.remove(user)
            self.save()
        if user not in self.users.distinct():
            self.users.add(user)
            self.save()
        return self
    
    #unsubscribe the user refuse of getting notifications
    def unsubscribe(self,user):
        self.users.remove(user)
        self.notified_users.remove(users)
        self.save()
        return self

    #mark user notified
    def notified(self,user):
        self.notified_users.remove(user)
        if user in self.users.distinct():
            self.users.remove(user)
            self.notified_users.add(user)
            self.save()
            return self
        else:
            self.users.add(user)
            self.save()
        return self

    #user commented one more time without subscription cancelation  
    #updating users field as being await for new notifications
    def update(self,user):
        #moving user from notified_users list to users to reach the notification
        if user in self.notified_users.distinct():
            self.users.add(user)
            self.notified_users.remove(user)
            self.save()
        #adding user to users list for its notification
        if user not in self.users.distinct():
            self.users.add(user)
            self.save()
        return self
    
    def get_real_object(self):
        """ gets real object for its announcemet"""
        real_object = self.content_type.model_class().objects.get(pk=str(self.object_pk))
        return real_object

    def get_content(self):
        """gets a real object for announcements"""
        real_object = self.get_real_object()
        content = ''
        if hasattr(real_object,'get_content'):
            content = real_object.get_content()
        return content or real_object
    
    def get_title(self):
        real_object = self.get_real_object()
        title = ''
        map = ['title','name','object_name']
        if hasattr(real_object,'get_title'):
            title = real_object.get_title()
        else:
            for m in map:
                if hasattr(real_object,m):
                    title = getattr(real_object,m)
                    break
                
        return title or real_object #if it has nor title in ['name','title','object_name'] nor get_title ;)

    def get_model(self):
        """gets a model name within get_model property or returns __str__"""
        real_object = self.get_real_object()
        if hasattr(real_object,'get_model'):
            return real_object.get_model()
        else:
            return real_object._meta.verbose_name

    def unsubscribe_link(self):
        """ return link for the announcement unsubscription"""
        return reverse('apps.core.views.delete_subscription',kwargs={'id':self.id})
    
class Settings(models.Model):
    user = models.ForeignKey(User, primary_key=True, related_name='user_settings_set')
    data = models.TextField(_('Decoded Data'),blank=True,null=True)
    #objects = SettingsManager()
    
    def encode(self,data_dict):
        pickled = pickle.dumps(data_dict)
        return base64.encodestring(pickled)
    
    #implement store,delete,update and get API for decoded settings
    def store_data(self,data_dict,blank=False):
        if not self.data:
            self.data = self.encode(data_dict)
        else:   
            _buffer_ = self.get_decoded()
            #deletes all data stored before
            if blank:
                _buffer_ = data_dict
            #updates all data
            else:
                _buffer_.update(data_dict)
            self.data = self.encode(_buffer_)
    
    def delete_key(self,key):
        _buffer_ = self.get_decoded()
        try:
            del _buffer_[key]
            self.data = self.encode(_buffer_)
        except:
            pass

    def get_decoded(self):
        if self.data:
            encoded_data = base64.decodestring(self.data)
            try:
                pickled = pickle.loads(encoded_data)
                return pickled
            except:
                return {}
        return {}
    
    settings = property(get_decoded,store_data)

    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

#makes a bug ?
from apps.core import signals
signals.setup_signals()
