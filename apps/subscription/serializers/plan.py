from rest_framework import serializers
from apps.subscription.models import Plan

class PlanReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plan
        fields = ["id","name","price","duration_days","max_products","max_invoices","max_staff","has_advanced_analytics","has_chat","has_api_access"]

