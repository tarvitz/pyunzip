# coding: utf-8
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

FAILURE_MESSAGES = {
    'wrong_owner_field': _(
        "You should use your own user id for owner field set")
}


class ModelAccessSerializerMixin(object):
    """
    ModelAccessSerializer restricts access for several fields which could not
    modify general users, for example ``ModelObject`` instance owner id.

    ex: picture.owner could not be set with another owner id
    """
    user_owner_fields = []

    def get_admin_perm(self):
        request = self.context['request']
        prefix = 'change'
        if request.method == 'POST':
            prefix = 'add'
        elif request.method in ('PUT', 'PATCH', ):
            prefix = 'change'
        elif request.method == 'DELETE':
            prefix = 'delete'
        app = self.Meta.model._meta.app_label
        model_name = self.Meta.model._meta.model_name
        perm = '%(app)s.%(prefix)s_%(model)s' % {
            'app': app,
            'model': model_name,
            'prefix': prefix
        }
        return perm

    def validate(self, attrs):
        request = self.context['request']
        perm = self.get_admin_perm()
        for field in self.user_owner_fields:
            value = attrs.get(field, None)
            if (value and request.user != value
                    and not request.user.has_perm(perm)):
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['wrong_owner_field'])
        return super(ModelAccessSerializerMixin, self).validate(attrs)


class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContentType