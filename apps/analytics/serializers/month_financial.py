from rest_framework import serializers
from apps.cost_month.models import MonthlyFinancialSummary
from apps.cost_category.models import MonthlyCostCategory

class CostCategoryBreakdownSerializer(serializers.ModelSerializer):
    category_name= serializers.CharField(source='cost_category__name',read_only=True)

    class Meta:
        model = MonthlyCostCategory
        fields=["category_name",'cost']

class MonthFinancialBreakdonwSerializer(serializers.ModelSerializer):
    cost_category_items=CostCategoryBreakdownSerializer(many=True,read_only=True)
    class Meta:
        model = MonthlyFinancialSummary
        fields=['taxes','salary_expenditure','products_total_cost','net_profit_after_tax','cost_category_items']

