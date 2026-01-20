from rest_framework import serializers

from apps.cost_category.models import MonthlyCostCategory
from .cost_category import  CostCategorySerializer


class MonthlyCostCategoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonthlyCostCategory
        fields = ['cost_category','cost']

class MonthlyAllCostCategoryCreateSerializer(serializers.Serializer):
    cost_category_items=MonthlyCostCategoryCreateSerializer(many=True)

class MonthlyCostCategoryReadSerializer(serializers.ModelSerializer):
    cost_category=CostCategorySerializer()
    class Meta:
        model = MonthlyCostCategory
        fields = ['id','cost_category','cost']

class MonthlyCostCategoryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonthlyCostCategory
        fields = ['cost_category','cost']
