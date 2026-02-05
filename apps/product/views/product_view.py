from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from apps.product.models import Product
from apps.product.serializers.product import ProductCreateSerializer, ProductUpdateSerializer, ProductReadSerializer
from apps.product.permission import ProductPermission
from apps.product.filters import ProductFilter
from apps.core.pagination import CursorPagination
from apps.core.cache import make_cache_key


class ProductViewSet(ModelViewSet):
    filter_backends =[DjangoFilterBackend]
    pagination_class = CursorPagination
    filterset_class = ProductFilter
    permission_classes = [ProductPermission]

    def get_queryset(self):
        return Product.objects.filter(
            business=self.request.user.business
        ).order_by("-created_at", "-id")


    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProductUpdateSerializer
        return ProductReadSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = Product.objects.create(
            name=data["name"],
            cost_price=data["cost_price"],
            base_price=data["base_price"],
            description=data["description"],
            product_category=data["product_category"],
            sku=data["sku"],
            input_gst_rate=data["input_gst_rate"],
            output_gst_rate=data["output_gst_rate"],
            business=request.user.business,
            created_by=request.user
        )
        cache.delete_pattern("")

        return Response(
            {
                "message": "Product created successfully",
                "product": {
                    "id": product.id,
                    "sku": product.sku,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        cache_key = make_cache_key(request, "product", "details", request.user)
        cache_data = cache.get(cache_key)
        if cache_data:
            return Response(cache_data)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60)
            return response

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*3)
        return Response(serializer.data, status=status.HTTP_200_OK)
