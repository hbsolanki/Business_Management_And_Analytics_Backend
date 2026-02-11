from rest_framework.routers import DefaultRouter
from apps.inventory.views import inventory_product_view,inventory_transaction_view

router = DefaultRouter()
router.register("stock", inventory_product_view.InventoryProductViewSet, basename="inventoryproduct")
router.register("transaction", inventory_transaction_view.InventoryTransactionViewSet, basename="inventorytransaction")

urlpatterns = router.urls