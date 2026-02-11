from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from apps.user.models import User
from apps.business.serializers import BusinesSerializer
from apps.base.serializers import BaseSerializer


class UserSerializer(BaseSerializer):
    business=BusinesSerializer(read_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id", "business", "first_name", "last_name", "email", "username", "role","work","salary","password", "mobile_number",
                  "profile_picture", "description", "date_joined"]
        read_only_fields = ["id", "date_joined", "business"]

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


    def update(self, instance, validated_data):

        request = self.context["request"]

        # if salary being updated
        if "salary" in validated_data:
            if not request.user.has_perm("user.can_update_salary"):
                raise serializers.ValidationError({
                    "salary": "You do not have permission to update salary"
                })
        if "work" in validated_data:
            if not request.user.has_perm("user.can_update_work"):
                raise serializers.ValidationError({"work": "You do not have permission to update work"})

        if "role" in validated_data:
            if validated_data["role"] == User.Role.OWNER and not request.user.has_perm("user.can_create_owner"):
                raise serializers.ValidationError({"details": "You do not have permission to create Owner"})
            if validated_data["role"]==User.Role.MANAGER and not request.user.has_perm("user.can_create_manager"):
                raise serializers.ValidationError({"role": "You do not have permission to create manager"})
            if validated_data["role"]==User.Role.EMPLOYEE and not request.user.has_perm("user.can_create_employee"):
                raise serializers.ValidationError({"role": "You do not have permission to create employee"})

        password = validated_data.pop("password", None)

        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

        return instance

    def create(self, validated_data):
        request = self.context["request"]
        if validated_data["role"]==User.Role.OWNER and not request.user.has_perm("user.can_create_owner"):
            raise serializers.ValidationError({"details": "You do not have permission to create Owner"})
        if validated_data["role"]==User.Role.MANAGER and not request.user.has_perm("user.can_create_manager"):
            raise serializers.ValidationError({"details": "You do not have permission to create manager"})
        elif validated_data["role"]==User.Role.EMPLOYEE and not request.user.has_perm("user.can_create_employee"):
            raise serializers.ValidationError({"details": "You do not have permission to create employee"})

        password = validated_data.pop("password")
        print(validated_data)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class OwnerCreateSerializer(UserSerializer):
    def create(self, validated_data):
        validated_data["role"] = User.Role.OWNER
        return super().create(validated_data)


class ManagerCreateSerializer(UserSerializer):
    def create(self, validated_data):
        validated_data["role"] = User.Role.MANAGER
        validated_data["business"] = self.context["request"].user.business
        return super().create(validated_data)


class EmployeeCreateSerializer(UserSerializer):
    def create(self, validated_data):
        validated_data["role"] = User.Role.EMPLOYEE
        validated_data["business"] = self.context["request"].user.business
        return super().create(validated_data)


class UserBasicDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields=["id","first_name","last_name","role","username","mobile_number","profile_picture","email"]

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

