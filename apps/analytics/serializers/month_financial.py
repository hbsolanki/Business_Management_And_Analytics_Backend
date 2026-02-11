from rest_framework import serializers
from apps.cost.models import MonthlyFinancialSummary
from apps.cost.models import MonthlyCostCategory

class CostCategoryBreakdownSerializer(serializers.ModelSerializer):
    category_name= serializers.CharField(source='cost_category.name',read_only=True)

    class Meta:
        model = MonthlyCostCategory
        fields=["category_name",'cost']

class MonthFinancialBreakdownSerializer(serializers.ModelSerializer):
    cost_category_items=CostCategoryBreakdownSerializer(many=True,read_only=True)
    class Meta:
        model = MonthlyFinancialSummary
        fields=['year','month','taxes','salary_expenditure','products_total_cost','net_profit_after_tax','cost_category_items']

