from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.product.models import Product
from apps.inventory.models import InventoryProduct
from apps.analytics.serializers.product import ProductDetailsSerializer,ProductStockSerializer,ProductPerformanceSerializer
from apps.analytics.serializers.filter import ProductPerformanceFilterSerializer
from apps.cost_month.models import MonthlyProductPerformance
from django_filters.rest_framework import DjangoFilterBackend
from apps.analytics.filters import ProductPerformanceMonthYearFilter,ProductPerformanceFilter
from django.db.models import Sum,F
from apps.user.permission import IsOwnerOrManager
from apps.invoice.models import Invoice
from drf_spectacular.utils import extend_schema

class AnalysisProductViewSet(GenericViewSet):
    permission_classes = [IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return MonthlyProductPerformance.objects.filter(monthly_summary__business=self.request.user.business)

    def get_filterset_class(self):
        if self.action == 'product_performance':
            return ProductPerformanceMonthYearFilter
        return None

    @extend_schema(summary="Get Product Details", responses={200: ProductDetailsSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="details")
    def product_details(self, request):
        products = Product.objects.all()
        serializer = ProductDetailsSerializer(products, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Get Product Stock", responses={200: ProductStockSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="stocks")
    def product_stocks(self, request):
        inventoryData = InventoryProduct.objects.select_related(
            "product", "product__product_category"
        )
        serializer = ProductStockSerializer(inventoryData, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Get Month Breakdown",parameters=[ProductPerformanceFilterSerializer],responses={200: ProductPerformanceSerializer})
    @action(detail=False, methods=["get"], url_path="performance")
    def product_performance(self, request):
        qs = Invoice.objects.filter(business=request.user.business)
        filterset = ProductPerformanceFilter(request.GET, queryset=qs)

        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        if not filterset.qs.exists():
            return Response({"error":"Data not found"}, status=400)
        data=filterset.qs.aggregate(
            total_quantity_sold=Sum("invoice_items__quantity"),
            total_revenue=Sum(F("invoice_items__quantity")*F("invoice_items__selling_price")),
            total_profit=Sum(F("invoice_items__quantity")*F("invoice_items__product__net_profit")),
            total_cost=Sum(F("invoice_items__quantity")*F("invoice_items__product__cost_price")),
        )

        serializer = ProductPerformanceSerializer(data)
        return Response(serializer.data,status=status.HTTP_200_OK)


