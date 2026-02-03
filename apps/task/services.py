from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.notification.models import Notification
from apps.notification.serializers import NotificationReadSerializer
from apps.task.models import Task


def send_notification(task: Task, request=None):
    notification = Notification.objects.create(
        user=task.assignee,
        actor=task.assigned_by,
        title=f"Task: {task.title}",
        content=f"New task assigned by {task.assigned_by.username}",
        action_type=Notification.ActionType.TASK_ASSIGNED,
        action_link=f"/task/{task.id}/",
    )

    serializer = NotificationReadSerializer(
        notification,
        context={"request": request} if request else {}
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notification_{notification.user.id}",
        {
            "type": "notification",
            **serializer.data,
        }
    )
