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
    def validate(self, attrs):
        request = self.context['request']
        privileged = request.user and request.user.has_perm(
            'karma.change_karma')
        if not privileged:
            offset = datetime.now() - timedelta(
                minutes=settings.KARMA_TIMEOUT_MINUTES)

            karmas = request.user.karma_voter_set.filter(date__gte=offset)
            check_methods = ['POST', 'PUT', ]
            if (request.method in check_methods
                    and karmas.count() >= settings.KARMA_PER_TIMEOUT_AMOUNT):
                raise serializers.ValidationError(FAILURE_MESSAGES['timeout'])

        return attrs

    def validate_voter(self, attrs, source):
        request = self.context['request']
        voter = attrs[source]
        if request.user != voter:
            privileged = request.user and request.user.has_perm(
                'karma.change_karma')
            if not privileged:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['karma_voter_violation']
                )
        return attrs

    def validate_user(self, attrs, source):
        request = self.context['request']
        if request.user == attrs[source]:
            raise serializers.ValidationError(
                FAILURE_MESSAGES['self_karma_set'])
        return attrs

    def validate_value(self, attrs, source):
        value = attrs[source]
        request = self.context['request']
        if value not in (-1, 1):
            privileged = request.user and request.user.has_perm(
                'karma.change_karma')
            if not privileged:
                raise serializers.ValidationError(
                    FAILURE_MESSAGES['karma_amount_exceed']
                )
        return attrs

    class Meta:
        model = Karma
        url_field_name = 'url_detail'
