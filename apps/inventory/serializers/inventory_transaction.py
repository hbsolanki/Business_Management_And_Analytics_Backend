from rest_framework import serializers
from apps.inventory.serializers.inventory_product import InventoryProductItemsSerializer
from apps.inventory.models import InventoryTransaction,InventoryTransactionItem

class InventoryTransactionItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product = InventoryProductItemsSerializer(read_only=True)
    class Meta:
        model = InventoryTransactionItem
        fields = ["id", "product_id", "quantity","product"]
        read_only_fields = ["id","product"]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    items=InventoryTransactionItemSerializer(many=True)
    class Meta:
        model = InventoryTransaction
        fields=["id","action","description","items","created_at","created_by"]
        read_only_fields = ["id","created_at","created_by"]
