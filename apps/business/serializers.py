from rest_framework import serializers
import re
from apps.business.models import Business

class BusinesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields=["id","name","gst_number","description"]
        read_only_fields = ["id"]

    def validate_gst_number(self, value):
        if value:
            pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("Invalid GST number format")
        return value


    def create(self, validated_data):
        return Business.objects.create(**validated_data)
