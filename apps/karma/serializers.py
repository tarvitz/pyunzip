# coding: utf-8
from apps.karma.models import Karma
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from django.conf import settings

FAILURE_MESSAGES = {
    'self_karma_set': _("You can not alter karma for yourself"),
    'karma_amount_exceed': _(
        "You can not set custom karma amount, use `-1` and `1` values only."
    ),
    'timeout': _(
        "Timeout. You have exceeded amount of karma modification, please wait"
    ),
    'karma_voter_violation': _(
        "You can not set another user for voting. Use your own id",
    )
}

__all__ = [
    'FAILURE_MESSAGES', 'KarmaSerializer'
]


class KarmaSerializer(serializers.HyperlinkedModelSerializer):
    site_url = serializers.CharField(source='url', read_only=True)
    url = serializers.CharField(source='get_api_absolute_url',
                                read_only=True)

    def validate(self, attrs):
        request = self.context['request']
        privileged = request.user and request.user.has_perm(
            'karma.change_karma')
        if not privileged:
            offset = datetime.now() - timedelta(
                minutes=settings.KARMA_TIMEOUT_MINUTES)

            karmas = request.user.karma_voter_set.filter(date__gte=offset)
            # apply check only for create methods, update ones should passes
            # normally
            create_methods = ['POST', 'PUT', ]
            if (request.method in create_methods
                    and karmas.count() >= settings.KARMA_PER_TIMEOUT_AMOUNT):
                raise serializers.ValidationError(FAILURE_MESSAGES['timeout'])

        return attrs

    def validate_voter(self, value):
        """ non-privileged user can not cast karma
        from different to his own user id """
        request = self.context['request']
        voter = value
        if request.user != voter:
            privileged = request.user and request.user.has_perm(
                'karma.change_karma')
            if not privileged:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['karma_voter_violation']
                )
        return value

    def validate_user(self, value):
        """ non-privileged user can not set karma for himself """
        request = self.context['request']
        if request.user == value:
            raise serializers.ValidationError(
                FAILURE_MESSAGES['self_karma_set'])
        return value

    def validate_value(self, value):
        """ non-privileged user can not set karma value amount more than its
        safe range with -1,1 """

        request = self.context['request']
        if value not in (-1, 1):
            privileged = request.user and request.user.has_perm(
                'karma.change_karma')
            if not privileged:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['karma_amount_exceed']
                )
        return value

    class Meta:
        model = Karma
