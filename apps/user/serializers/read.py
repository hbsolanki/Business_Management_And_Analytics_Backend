from rest_framework import serializers
from apps.user.models import User
from apps.business_app.serializers import OnwerBusinessReadSerializer, BusinessReadSerializer
from apps.user.serializers.base import BaseUserReadSerializer

class UserReadSerializer(BaseUserReadSerializer):
    business = BusinessReadSerializer()

    class Meta(BaseUserReadSerializer.Meta):
        fields = BaseUserReadSerializer.Meta.fields + ["business"]

class OwnerUserReadSerializer(BaseUserReadSerializer):
    business = OnwerBusinessReadSerializer()

    class Meta(BaseUserReadSerializer.Meta):
        fields = BaseUserReadSerializer.Meta.fields + ["business"]

class UserNormalDetailsReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profile_picture", "username", "business"]
