from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.cost.models import MonthlyCostCategory, MonthlyFinancialSummary, CostCategory
from apps.cost.serializers.cost_category import CostCategorySerializer


class MonthlyCostCategoryWriteSerializer(serializers.ModelSerializer):
    cost_category = serializers.PrimaryKeyRelatedField(queryset=CostCategory.objects.all())

    class Meta:
        model = MonthlyCostCategory
        fields = ["cost_category", "cost"]

class MonthlyAllCostCategoryCreateSerializer(serializers.Serializer):
    cost_category_items = MonthlyCostCategoryWriteSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        items = validated_data["cost_category_items"]
        today = timezone.now()

        with transaction.atomic():
            monthly_summary, _ = MonthlyFinancialSummary.objects.get_or_create(
                business=user.business,
                year=today.year,
                month=today.month,
            )

            existing_map = {
                obj.cost_category_id: obj
                for obj in MonthlyCostCategory.objects.filter(
                    monthly_summary=monthly_summary
                )
            }

            to_create = []
            to_update = []

            for item in items:
                category = item["cost_category"]
                cost = item["cost"]

                if category.id in existing_map:
                    obj = existing_map[category.id]
                    if obj.cost != cost:
                        obj.cost = cost
                        to_update.append(obj)
                else:
                    to_create.append(
                        MonthlyCostCategory(
                            monthly_summary=monthly_summary,
                            cost_category=category,
                            cost=cost,
                        )
                    )

            if to_create:
                MonthlyCostCategory.objects.bulk_create(to_create)

            if to_update:
                MonthlyCostCategory.objects.bulk_update(to_update, ["cost"])

        return monthly_summary


class MonthlyCostCategoryReadSerializer(serializers.ModelSerializer):
    cost_category = CostCategorySerializer(read_only=True)

    class Meta:
        model = MonthlyCostCategory
        fields = ["id", "cost_category", "cost"]
