from rest_framework import serializers
from apps.product.models import Product
from apps.product.serializers.product_category import ProductCategorySerializer

class ProductBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["name","base_price","cost_price","description","product_category","sku","input_gst_rate","output_gst_rate"]

    def validate_sku(self, value):
        qs = Product.objects.filter(sku=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Product SKU already exists")

        return value


class ProductCreateSerializer(ProductBaseSerializer):
    pass


class ProductUpdateSerializer(ProductBaseSerializer):
    pass


class ProductReadSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(read_only=True)
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "base_price", "cost_price", "description", "product_category", "stock_quantity","sku", "input_gst_rate",
                  "output_gst_rate", "net_profit", "created_at", "updated_at"]

    def get_stock_quantity(self, obj):
        inventory_product = obj.inventory_product.first()
        if inventory_product:
            return inventory_product.stock_quantity
        return None


class ProductReadInventorySerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "product_category", "sku", ]


