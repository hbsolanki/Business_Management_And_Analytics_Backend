from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from apps.inventory.models import InventoryTransaction, Inventory
from apps.inventory.serializers import create, read
from apps.inventory.services.inventory_transaction_service import create_inventory_transaction
from apps.inventory.permission import InventoryPermission
from apps.inventory.filters import InventoryTransactionFilter
from apps.core.pagination import CursorPagination


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InventoryTransactionFilter
    pagination_class = CursorPagination

    def get_inventory(self):

        try:
            return Inventory.objects.get(business=self.request.user.business)
        except Inventory.DoesNotExist:
            raise ValidationError("Inventory not found")

    def get_queryset(self):
        return InventoryTransaction.objects.filter(inventory=self.get_inventory()).prefetch_related("items__product").order_by("-created_at","-id").distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return create.InventoryTransCreateSerializer

        return read.InventoryTransReadSerializer

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

