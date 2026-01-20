from rest_framework import serializers
from apps.customer.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(
        choices=[("male", "male"), ("female", "female")]
    )

    class Meta:
        model = Customer
        fields = ["id","name", "mobile_number", "gender", "age", "address", "email"]
        read_only_fields = ["id"]
