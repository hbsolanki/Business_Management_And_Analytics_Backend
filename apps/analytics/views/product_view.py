from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.product.models import Product
from apps.inventory.models import InventoryProduct
from apps.analytics.serializers.product import (
    ProductDetailsSerializer,
    ProductStockSerializer,
)
from apps.cost_month.models import MonthlyProductPerformance
from django_filters.rest_framework import DjangoFilterBackend
from apps.analytics.filters import ProductPerformanceMonthYearFilter
from django.db.models import Sum
from apps.user.permission import IsOwnerOrManager

class AnalysisProductViewSet(GenericViewSet):
    permission_classes = [IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return MonthlyProductPerformance.objects.filter(monthly_summary__business=self.request.user.business)

    def get_filterset_class(self):
        if self.action == 'product_performance':
            return ProductPerformanceMonthYearFilter
        return None


    @action(detail=False, methods=["get"], url_path="details")
    def product_details(self, request):
        products = Product.objects.all()
        serializer = ProductDetailsSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stocks")
    def product_stocks(self, request):
        inventoryData = InventoryProduct.objects.select_related(
            "product", "product__product_category"
        )
        serializer = ProductStockSerializer(inventoryData, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="performance")
    def product_performance(self, request):
        queryset = self.get_queryset()

        filterset = ProductPerformanceMonthYearFilter(
            request.GET,
            queryset=queryset,
        )

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        qs = filterset.qs
        print(str(qs.query))

        if not qs.exists():
            return Response({"detail": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

        data = (
            qs.select_related("product")
            .values("product_id", "product__name", "product__sku")
            .annotate(
                total_quantity=Sum("quantity"),
                total_cost=Sum("cost"),
                total_revenue=Sum("revenue"),
            )
        )

        return Response(list(data), status=status.HTTP_200_OK)
