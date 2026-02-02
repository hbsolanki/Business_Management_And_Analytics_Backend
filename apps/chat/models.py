from apps.core.model import BaseModel
from django.db import models
from apps.user.models import User

class Conversation(BaseModel):
    user1 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_user1')
    user2 = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_user2')

    class Meta:
        db_table = 'bma_conversation'
        constraints = [
            models.UniqueConstraint(fields=["user1", "user2"],condition=models.Q(is_deleted=False),name="unique_active_conversation_users")]

class Message(BaseModel):
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='conversation_messages')
    text=models.TextField(blank=True,null=True)
    is_updated=models.BooleanField(default=False)
    deleted_text=models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'bma_message'
        ordering = ['-created_at']

class BroadcastGroup(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_broadcast_group')
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'bma_broadcast_group'

class BroadcastGroupMember(BaseModel):
    user_member = models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_broadcast_group_member')
    broadcast_group = models.ForeignKey(BroadcastGroup,on_delete=models.CASCADE,related_name='broadcast_group_members')

    class Meta:
        db_table = 'bma_broadcast_group_member'

