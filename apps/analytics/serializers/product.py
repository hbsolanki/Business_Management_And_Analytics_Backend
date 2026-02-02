from rest_framework import serializers
from apps.inventory.models import InventoryProduct
from apps.product.models import Product

class ProductDetailsSerializer(serializers.ModelSerializer):
    product_category = serializers.CharField(source="product_category.name", read_only=True)
    class Meta:
        model = Product
        fields=["name","cost_price","base_price","net_profit","product_category"]



class ProductStockSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)
    product_category = serializers.CharField(source="product.product_category.name", read_only=True)

    class Meta:
        model = InventoryProduct
        fields = ["id", "name","product_category", "stock_quantity"]


class ProductSellingSerializer(serializers.ModelSerializer):
    pass


class ProductPerformanceSerializer(serializers.Serializer):
    total_quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
