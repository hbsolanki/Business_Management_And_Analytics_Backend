from apps.user.serializers.user import UserBasicDetailsSerializer
from rest_framework import serializers
from apps.user.models import User
from django.db import transaction
from django.db.models import Q

from apps.chat.models import Conversation


class ConversationGetOrCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(write_only=True)

    def validate_user_id(self, value):
        request = self.context["request"]

        if value == request.user.id:
            raise serializers.ValidationError("Cannot chat with yourself")

        try:
            self.other_user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        return value

    def create(self, validated_data):
        request = self.context["request"]
        user1, user2 = request.user, self.other_user

        if user1.id > user2.id:
            user1, user2 = user2, user1

        conversation, created = Conversation.objects.get_or_create(
            user1=user1,
            user2=user2
        )

        return conversation


class ConversationBulkIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_ids(self, value):
        user = self.context["request"].user

        qs = Conversation.objects.filter(id__in=value).filter(
            Q(user1=user) | Q(user2=user)
        )

        if qs.count() != len(value):
            raise serializers.ValidationError("some ids not found or not allowed")

        self.qs = qs
        return value

    @transaction.atomic
    def save(self, **kwargs):
        self.qs.update(is_deleted=True, is_active=False)
        return {"detail": "conversations deleted"}

class ConversationReadSerializer(serializers.ModelSerializer):
    user1 = UserBasicDetailsSerializer(read_only=True)
    user2 = UserBasicDetailsSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'user1', 'user2']


