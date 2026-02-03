from django.db import models
from apps.user.models import User
from apps.core.model import BaseModel

class Notification(BaseModel):

    class ActionType(models.TextChoices):
        TASK_ASSIGNED = "TASK_ASSIGNED", "Task Assigned"
        TASK_UPDATED = "TASK_UPDATED", "Task Updated"
        COMMENT = "COMMENT", "Comment"
        SYSTEM = "SYSTEM", "System"



    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    actor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='triggered_notifications')
    title = models.CharField(max_length=100)
    content = models.TextField()
    action_type=models.CharField(max_length=50,choices=ActionType.choices,null=True,blank=True)
    action_link = models.TextField(null=True,blank=True)
    is_read = models.BooleanField(default=False)


    class Meta:
        db_table = 'bma_notification'
        ordering = ["-created_at"]