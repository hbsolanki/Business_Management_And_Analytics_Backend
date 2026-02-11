from rest_framework import serializers
from apps.cost.models import CostCategory

class CostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCategory
        fields = ["id", "name", "description", "business"]
        read_only_fields = ["id", "business"]
