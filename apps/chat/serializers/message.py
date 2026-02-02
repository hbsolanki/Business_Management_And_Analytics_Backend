from rest_framework import serializers
from apps.chat.models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id")

    class Meta:
        model = Message
        fields = ["id", "sender_id", "text", "created_at","is_updated"]

class MessageByConversationResponseSerializer(serializers.ModelSerializer):
    pass