from rest_framework import serializers
from apps.user.models import User
from .base import BaseUserCreateSerializer

class ManagerCreateSerializer(BaseUserCreateSerializer):
    pass

class EmployeeCreateSerializer(BaseUserCreateSerializer):
    work = serializers.ChoiceField(choices=User.Work.choices, required=False, allow_null=True)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = BaseUserCreateSerializer.Meta.fields + ["work"]

class OwnerCreateSerializer(BaseUserCreateSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=["first_name","last_name","mobile_number","username","password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)