from django.core.cache import cache
from rest_framework import viewsets, status,mixins
from apps.base.permission.model_permissions import ModelPermissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.inventory.models import InventoryTransaction, Inventory
from apps.inventory.utils.inventory_transaction_service import create_inventory_transaction
from apps.inventory.filters import InventoryTransactionFilter
from apps.base.pagination import CursorPagination
from apps.inventory.serializers.inventory_transaction import InventoryTransactionSerializer


class InventoryTransactionViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    permission_classes = [ModelPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InventoryTransactionFilter
    pagination_class = CursorPagination
    serializer_class = InventoryTransactionSerializer

    def get_inventory(self):
        inventory, _ = Inventory.objects.get_or_create(
            business=self.request.user.business
        )
        return inventory

    def get_queryset(self):
        inventory = self.get_inventory()
        cache_key = f"inventory:{inventory.id}:inventory_transaction"
        data = cache.get(cache_key)
        if data:
            return data
        data = InventoryTransaction.objects.filter(inventory=self.get_inventory()).prefetch_related("items__product").order_by("-created_at","-id").distinct()
        cache.set(cache_key, data, timeout=60 * 2)
        return data


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction = create_inventory_transaction(
            inventory=self.get_inventory(),
            action=serializer.validated_data["action"],
            description=serializer.validated_data["description"],
            items=serializer.validated_data["items"],
            user=request.user,
        )

        return Response(
            {
                "message": "Transaction completed",
                "transaction_id": transaction.id,
            },
            status=status.HTTP_201_CREATED,
        )

