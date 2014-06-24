# coding: utf-8
from apps.tabletop.models import Codex, Roster, Report, Mission, Game
from rest_framework import serializers
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _


__all__ = [
    'CodexSerializer', 'RosterSerializer', 'ReportSerializer',
    'MissionSerializer', 'GameSerializer'
]

FAILURE_MESSAGES = {
    'wrong_owner': _("You should use your own user id for owner field set"),
    'wrong_winner_rosters': _("There's no such winner `%s` in rosters")
}


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


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(required=False,
                                                view_name='user-detail')

    def validate_owner(self, attrs, source):
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
        owner = attrs[source]
        if not(request.user and request.user.has_perm(perm)):
            if owner is None:
                attrs[source] = request.user
            elif owner != request.user:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['wrong_owner']
                )
        return attrs

    def validate(self, attrs):
        winners = attrs.get('winners', [])
        rosters = attrs.get('rosters', [])
        msg_list = []
        for winner in winners:
            if winner not in rosters:
                msg = FAILURE_MESSAGES['wrong_winner_rosters'] % winner
                msg_list.append(msg)
        if msg_list:
            self._errors['winners'] = ErrorList(msg_list)
        return attrs

    class Meta:
        model = Report


class GameSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = Game


class MissionSerializer(serializers.HyperlinkedModelSerializer):
    # todo: investigate why hyperlinked serializer fails on post/put game data
    game = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Mission
