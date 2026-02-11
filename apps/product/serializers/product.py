from rest_framework import serializers
from apps.product.models import Product
from apps.product.serializers.product_category import ProductCategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerializer(read_only=True)
    stock_quantity = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = ["id","name","base_price","cost_price","description","product_category","sku","input_gst_rate","output_gst_rate","stock_quantity","net_profit","created_at","updated_at"]
        read_only_fields = ["id","stock_quantity","net_profit","created_at","updated_at"]

    def validate_sku(self, value):
        qs = Product.objects.filter(sku=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Product SKU already exists")

        return value

    def get_stock_quantity(self, obj):
        inventory_product = obj.inventory_product.first()
        if inventory_product:
            return inventory_product.stock_quantity
        return None

    def create(self, validated_data):
        request = self.context.get("request")
        business = request.user.business,
        created_by = request.user
        validated_data["business"] = business
        validated_data["created_by"] = created_by
        return Product.objects.create(**validated_data)



