from rest_framework import serializers
from apps.business.models import Business
from apps.user.serializers.base import BaseUserSerializer
from apps.user.models import User


class BusinessCreateSerializer(BaseUserSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    first_name = serializers.CharField(max_length=150,required=True)
    last_name = serializers.CharField(max_length=150,required=True)
    username = serializers.CharField(max_length=150,required=True)
    password = serializers.CharField(write_only=True,required=True)
    mobile_number = serializers.CharField()

    class Meta:
        model = Business
        fields=['name','description','first_name','last_name','username','password','mobile_number']


class BusinessReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields=['id','name','description']


class OnwerBusinessReadSerializer(BusinessReadSerializer):

    class Meta:
        model = Business
        fields = BusinessReadSerializer.Meta.fields+[ 'haveEquity', 'assets']


class UpdateBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['name','assets','haveEquity','description']


class BusinessUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields=["id","username","profile_picture","first_name","last_name","email","mobile_number","role"]
