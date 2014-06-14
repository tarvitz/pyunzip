# coding: utf-8
from apps.tabletop.models import Codex, Roster
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class CodexSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.SerializerMethodField('get_content_type')

    def get_content_type(self, instance):
        return instance.content_type.pk

    class Meta:
        model = Codex
        #exclude = ('content_type', )


class RosterSerializer(serializers.HyperlinkedModelSerializer):
    codex = serializers.HyperlinkedRelatedField(required=True,
                                                view_name='codex-detail')
    owner = serializers.HyperlinkedRelatedField(required=False,
                                                view_name='user-detail')

    def restore_object(self, attrs, instance=None):
        if not attrs.get('owner'):
            attrs.update({'owner': self.context['request'].user})
        return super(RosterSerializer, self).restore_object(attrs, instance)

    def save_object(self, obj, **kwargs):
        """
        It does not matter if user would pass wrong owner id,
        anyway roster should be saved with his/hers one.

        :param obj:
        :param kwargs:
        :return:
        """
        request = self.context['request']
        if not request.user.has_perm('tabletop.change_roster'):
            obj.owner = self.context['request'].user
        return super(RosterSerializer, self).save_object(obj, **kwargs)

    class Meta:
        model = Roster
        exclude = ('roster_cache', )
