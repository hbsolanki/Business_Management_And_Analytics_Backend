from django.db import models
from django.core.validators import MinValueValidator
from apps.business.models import Business
from apps.base.models import BaseModel
from apps.product.models import Product

class Inventory(models.Model):
    business=models.OneToOneField(to=Business, on_delete=models.CASCADE)

    class Meta:
        db_table="bma_inventory"
        indexes=[models.Index(fields=["business"])]
        constraints = [
            models.UniqueConstraint(fields=["business"], name="unique_inventory_business")]


class InventoryProduct(BaseModel):
    inventory=models.ForeignKey(to=Inventory, on_delete=models.CASCADE,related_name="inventory_product_item")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,related_name="inventory_product")
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        db_table="bma_inventory_product"
        indexes=[models.Index(fields=["inventory"])]
        constraints = [
            models.UniqueConstraint(fields=["inventory", "product"],name="unique_inventory_product") ]

class InventoryTransaction(BaseModel):

    class Action(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"

    action=models.CharField(max_length=10,choices=Action.choices)
    description=models.CharField(max_length=200)
    inventory=models.ForeignKey(Inventory,on_delete=models.CASCADE,related_name="inventory_transactions")

    class Meta:
        db_table="bma_inventory_transaction"
        indexes = [
            models.Index(fields=["inventory"]),
            models.Index(fields=["created_at"]),
        ]

class InventoryTransactionItem(models.Model):
    transaction=models.ForeignKey(InventoryTransaction,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table="bma_inventory_transaction_item"
        indexes=[models.Index(fields=["transaction"])]