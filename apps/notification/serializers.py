from rest_framework import serializers

from apps.notification.models import Notification
from apps.business_app.serializers import BusinessUserSerializer


class NotificationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = []


class NotificationReadSerializer(serializers.ModelSerializer):
    user=BusinessUserSerializer(read_only=True)
    actor = BusinessUserSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = ["id","user","actor","title","content","action_type","action_link","is_read","created_at"]

class NotificationBulkReadSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_ids(self, value):
        qs = Notification.objects.filter(id__in=value)
        if qs.count() != len(set(value)):
            raise serializers.ValidationError(
                "One or more notification IDs are invalid."
            )
        return value