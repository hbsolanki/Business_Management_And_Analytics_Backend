from rest_framework import serializers
from apps.task.models import Task
from apps.user.models import User


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id=serializers.IntegerField()

    class Meta:
        model = Task
        fields=["assignee_id","title","description"]

class BasicUserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields=["id","username","email","first_name","last_name","profile_picture","role","work"]

class TaskReadSerializer(serializers.ModelSerializer):
    assignee=BasicUserDetailsSerializer(read_only=True)
    assigned_by=BasicUserDetailsSerializer(read_only=True)

    class Meta:
        model = Task
        fields=["id","business","assignee","assigned_by","status","title","description","remarks","completed_at","created_at"]

class TaskUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields=["title","description","remarks","status"]
