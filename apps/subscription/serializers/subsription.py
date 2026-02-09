from rest_framework import serializers
from apps.subscription.models import Usage, Subscription
from .plan import PlanReadSerializer

class SubscriptionReadSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan_name",
            "price",
            "duration_days",

            "max_products",
            "max_invoices",
            "max_staff",
            "has_advanced_analytics",
            "has_chat",
            "has_api_access",

            "start_date",
            "end_date",
            "remaining_days",
            "status",

            "is_trial",
            "is_active",
        ]

    def get_remaining_days(self, obj):
        from django.utils import timezone
        delta = obj.end_date - timezone.now()
        return max(delta.days, 0)

    def get_status(self, obj):
        from django.utils import timezone

        if not obj.is_active:
            return "cancelled"

        if obj.end_date < timezone.now():
            return "expired"

        return "active"


class SubscriptionCreateSerializer(serializers.Serializer):
    plan_id=serializers.IntegerField()

class PlanUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usage
        fields = ["id","subscription_id","product_created","invoices_created","staff_created"]
