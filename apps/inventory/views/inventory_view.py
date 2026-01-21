from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.core.pagination import CursorPagination
from apps.inventory.permission import InventoryPermission
from apps.inventory.models import Inventory
from apps.inventory.serializers import read
from rest_framework.exceptions import ValidationError


class InventoryViewSet(viewsets.GenericViewSet):
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend]
    pagination_class = CursorPagination

    def get_inventory(self, user):
        try:
            return Inventory.objects.get(business=user.business)
        except Inventory.DoesNotExist:
            raise ValidationError("Inventory not found")

    def list(self, request):
        inventory = self.get_inventory(request.user)
        serializer = read.InventoryReadSerializer(inventory)
        return Response(serializer.data, status=status.HTTP_200_OK)
