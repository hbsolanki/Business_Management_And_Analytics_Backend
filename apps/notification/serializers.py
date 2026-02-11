from rest_framework import serializers

from apps.notification.models import Notification
from apps.user.serializers.user import UserBasicDetailsSerializer

class NotificationReadSerializer(serializers.ModelSerializer):
    user=UserBasicDetailsSerializer(read_only=True)
    actor = UserBasicDetailsSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = ["id","user","actor","title","content","action_type","action_link","is_read","created_at"]
        read_only_fields = ["id","user","actor","title","content","action_type","action_link","is_read","created_at"]

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