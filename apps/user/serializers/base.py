# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from rest_framework import serializers
# from apps.user.models import User
# from apps.business.serializers import BusinesSerializer
#
#
# class BaseUserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     business=BusinesSerializer()
#     def validate_username(self, value):
#         queryset = User.objects.filter(username=value)
#         if self.instance:
#             queryset = queryset.exclude(pk=self.instance.pk)
#         if queryset.exists():
#             raise serializers.ValidationError("Username already exists")
#         return value
#
#     def validate_mobile_number(self, value):
#         if not value.isdigit() or len(value) != 10:
#             raise serializers.ValidationError("Mobile number must be exactly 10 digits")
#         queryset = User.objects.filter(mobile_number=value)
#         if self.instance:
#             queryset = queryset.exclude(pk=self.instance.pk)
#         if queryset.exists():
#             raise serializers.ValidationError("Mobile number already exists")
#         return value
#
#     def validate_password(self, value):
#         try:
#             validate_password(value)
#         except ValidationError as exc:
#             raise serializers.ValidationError(exc.messages)
#         return value
#
#     class Meta:
#         model = User
#         fields=["id","business","first_name", "last_name", "email", "username","password","mobile_number","profile_picture","description","role","date_joined"]
#         read_only_fields=["id","role","date_joined","business"]
#
# class EmployeeOrManagerBaseSerializer(BaseUserSerializer):
#
#     class Meta(BaseUserSerializer.Meta):
#         model = User
#         fields = BaseUserSerializer.Meta.fields + ["work", "description", "salary", "created_by", "updated_by", "updated_at"]
#         read_only_fields = ["id","role","date_joined","salary","work","created_by","updated_by","updated_at"]
