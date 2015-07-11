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


class CurrentUserSerializerMixin(object):
    """
    check permission and set user field to current user
    """
    check_permission = 'auth.change_user'
    check_fields = []

    def _get_user_field(self, user):
        """
        get roster owner, if None or permission set can not change owner
        there should return current user

        :param user: owner
        :rtype: apps.accounts.models.User
        :return: owner user
        """
        request = self._context['request']
        if request.user.has_perm(self.check_permission):
            return user and user or request.user
        return request.user

    def _process_validated_data(self, validated_data):
        """
        update validated data with proper owner object and other things

        :param dict validated_data: validated data for update/create actions
        :rtype: dict
        :return: validated data
        """
        validated_data.update({
            field: self._get_user_field(validated_data.get(field))
            for field in self.check_fields
        })
        return validated_data


class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContentType