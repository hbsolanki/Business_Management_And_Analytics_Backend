from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.inventory.models import InventoryProduct, Inventory
from apps.inventory.serializers.read import InventoryProductReadSerializer
from apps.inventory.permission import  InventoryPermission
from apps.inventory.filters import InventoryProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.pagination import  CursorPagination
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from apps.core.cache import make_cache_key


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
        inventory = self.get_inventory()
        return (
            InventoryProduct.objects
            .filter(inventory=inventory)
            .select_related("product")
            .order_by("-created_at", "-id")
        )

    def list(self, request, *args, **kwargs):
        cache_key =make_cache_key(request, "inventory","stock",request.user)
        cache_data=cache.get(cache_key)
        if cache_data:
            return Response(cache_data)

        queryset=self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response=self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60)
            return response

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60)
        return Response(serializer.data, status=status.HTTP_200_OK)
