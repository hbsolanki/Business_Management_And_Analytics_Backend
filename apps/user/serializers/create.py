from rest_framework import serializers
from apps.user.models import User
from .base import BaseUserCreateSerializer

class ManagerCreateSerializer(BaseUserCreateSerializer):
    pass

class EmployeeCreateSerializer(BaseUserCreateSerializer):
    work = serializers.ChoiceField(choices=User.Work.choices, required=False, allow_null=True)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = BaseUserCreateSerializer.Meta.fields + ["work"]
