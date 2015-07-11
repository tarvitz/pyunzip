# coding: utf-8
from apps.accounts.models import User
from apps.tabletop.models import Codex, Roster, Report, Mission, Game
from apps.core.serializers import CurrentUserSerializerMixin

from rest_framework import serializers
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

__all__ = [
    'CodexSerializer', 'RosterSerializer', 'ReportSerializer',
    'MissionSerializer', 'GameSerializer'
]

FAILURE_MESSAGES = {
    'wrong_owner': _("You should use your own user id for owner field set"),
    'wrong_winner_rosters': _("There's no such winner `%s` in rosters")
}


class CodexSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        read_only=False,
        queryset=ContentType.objects.filter(app_label='wh',
                                            model='side'))

    class Meta:
        model = Codex


class RosterSerializer(CurrentUserSerializerMixin,
                       serializers.HyperlinkedModelSerializer):
    codex = serializers.HyperlinkedRelatedField(required=True,
                                                queryset=Codex.objects,
                                                view_name='codex-detail')
    owner = serializers.HyperlinkedRelatedField(
        required=False, read_only=False, view_name='user-detail',
        queryset=User.objects
    )
    check_fields = ['owner']
    check_permission = 'tabletop.change_roster'

    def update(self, instance, validated_data):
        self._process_validated_data(validated_data)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        It does not matter if user would pass wrong owner,
        anyway roster should be save with his own id.

        :param validated_data:
        :return:
        """
        self._process_validated_data(validated_data)
        return Roster.objects.create(**validated_data)

    class Meta:
        model = Roster
        exclude = ('roster_cache', )


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        read_only=False, queryset=User.objects,
        view_name='user-detail',
        default=None
    )

    def validate_owner(self, value):
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
        owner = value
        if not(request.user and request.user.has_perm(perm)):
            if owner is None:
                value = request.user
            elif owner != request.user:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['wrong_owner']
                )
        return value

    def validate(self, attrs):
        winners = attrs.get('winners', [])
        rosters = attrs.get('rosters', [])
        msg_list = []
        for winner in winners:
            if winner not in rosters:
                msg = FAILURE_MESSAGES['wrong_winner_rosters'] % winner
                msg_list.append(msg)
        if msg_list:
            raise serializers.ValidationError(ErrorList(msg_list))
        return attrs

    class Meta:
        model = Report


class GameSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = Game


class MissionSerializer(serializers.HyperlinkedModelSerializer):
    # todo: investigate why hyperlinked serializer fails on post/put game data
    game = serializers.PrimaryKeyRelatedField(
        read_only=False,
        queryset=Game.objects
    )

    class Meta:
        model = Mission
