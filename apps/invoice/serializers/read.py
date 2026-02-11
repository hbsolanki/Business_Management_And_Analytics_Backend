from rest_framework import serializers

from apps.invoice.models import ProductInvoice,Invoice
from apps.product.models import Product
from apps.customer.serializers import CustomerSerializer


class ProductInvoiceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields=["id","name","base_price"]

class ProductInvoiceItemReadSerializer(serializers.ModelSerializer):
    product=ProductInvoiceReadSerializer()

    class Meta:
        model = ProductInvoice
        fields=["id","product","quantity","base_price","selling_price"]

class InvoiceReadSerializer(serializers.ModelSerializer):
    invoice_items =ProductInvoiceItemReadSerializer(many=True)
    customer = CustomerSerializer()
    created_by = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Invoice
        fields=["id","business","customer","invoice_items","payment_mode","total_amount","sub_total","payment_date","created_at","created_by"]