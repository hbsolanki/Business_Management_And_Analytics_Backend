from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from apps.user.models import User

USER_BASE_FIELDS = ["first_name", "last_name", "email", "username", "mobile_number"]
USER_READ_EXTRA_FIELDS = ["id", "profile_picture", "role", "work", "description", "date_joined", "created_by", "updated_by", "updated_at"]
USER_CREATE_EXTRA_FIELDS = ["password", "salary", "description"]
USER_UPDATE_EXTRA_FIELDS = ["password", "profile_picture", "description"]

class BaseUserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_mobile_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be exactly 10 digits")
        queryset = User.objects.filter(mobile_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Mobile number already exists")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    class Meta:
        model = User


class BaseUserCreateSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = USER_BASE_FIELDS + USER_CREATE_EXTRA_FIELDS


class BaseUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = USER_BASE_FIELDS + USER_READ_EXTRA_FIELDS


class BaseUserUpdateSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = USER_BASE_FIELDS + USER_UPDATE_EXTRA_FIELDS

