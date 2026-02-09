from rest_framework import serializers

from apps.chat.models import Conversation
from apps.business.serializers import BusinessUserSerializer


class ConversationGetOrCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class ConversationGetOrCreateResponseSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    created = serializers.BooleanField


class ConversationBulkIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(),allow_empty=False)

class ConversationReadSerializer(serializers.ModelSerializer):
    user1 = BusinessUserSerializer(read_only=True)
    user2 = BusinessUserSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'user1', 'user2']
