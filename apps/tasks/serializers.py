from datetime import timezone

from rest_framework import serializers
from apps.tasks.models import Task
from apps.user.models import User
from apps.user.serializers.user import UserBasicDetailsSerializer
from apps.base.serializers import BaseSerializer


class TaskSerializer(BaseSerializer):
    assignee_id=serializers.IntegerField()
    assignee = UserBasicDetailsSerializer(read_only=True)
    assigned_by = UserBasicDetailsSerializer(read_only=True)

    class Meta:
            model = Task
            fields=["id","business","assignee_id","title","description","assignee","assigned_by","status","title","description","remarks","completed_at","created_at"]
            read_only_fields=["id","business","assignee","assigned_by","completed_at","created_at"]


    def create(self, validated_data):
        request = self.context.get("request")
        assignee=User.objects.filter(id=validated_data["assignee_id"]).first()

        return Task.objects.create(assignee=assignee,assigned_by=request.user,title=validated_data["title"],description=validated_data["description"])


    def update(self, instance, validated_data):
        if "status" in validated_data and validated_data["status"] == Task.Status.COMPLETED:
            instance.completed_at = timezone.now()

        return super().update(instance, validated_data)


