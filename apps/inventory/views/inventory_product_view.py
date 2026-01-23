from rest_framework import viewsets
from apps.inventory.models import InventoryProduct, Inventory
from apps.inventory.serializers.read import InventoryProductReadSerializer
from apps.inventory.permission import  InventoryPermission
from apps.inventory.filters import InventoryProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.pagination import  CursorPagination
from rest_framework.exceptions import ValidationError


class InventoryProductViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InventoryProductFilter
    pagination_class = CursorPagination
    serializer_class = InventoryProductReadSerializer

    def get_inventory(self):
        try:
            return Inventory.objects.get(business=self.request.user.business)
        except Inventory.DoesNotExist:
            raise ValidationError("Inventory not found")

    def get_queryset(self):
        return  InventoryProduct.objects.filter(inventory=self.get_inventory()).select_related("product").order_by("-created_at")
