# apps/chat/send_notification.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.chat.models import Message

def send_message(*, conversation, sender, text):
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        text=text
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{conversation.id}",
        {
            "type": "chat_message",
            "id": message.id,
            "sender": sender.id,
            "text": message.text,
            "created_at": message.created_at.isoformat(),
        }
    )

    return message
