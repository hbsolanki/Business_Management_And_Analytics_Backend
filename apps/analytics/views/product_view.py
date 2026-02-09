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
from apps.analytics.filters import ProductPerformanceMonthYearFilter,ProductPerformanceFilter,MonthlySummaryCreatedAtRangeFilter
from django.db.models import Sum,F
from apps.user.permission import IsOwnerOrManager
from apps.invoice.models import Invoice,ProductInvoice
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
from apps.core.cache import make_cache_key

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
        cache_key = make_cache_key(request, "analytics","product_details", request.user)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data,status=status.HTTP_200_OK)

        products = Product.objects.filter(business=request.user.business)
        serializer = ProductDetailsSerializer(products, many=True)
        cache.set(cache_key, serializer.data, 60*5)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Get Product Stock", responses={200: ProductStockSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="stocks")
    def product_stocks(self, request):
        cache_key = make_cache_key(request, "analytics","product_stocks", request.user)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data,status=status.HTTP_200_OK)

        inventoryData = InventoryProduct.objects.filter(business=request.user.business).select_related(
            "product", "product__product_category"
        )
        serializer = ProductStockSerializer(inventoryData, many=True)
        cache.set(cache_key, serializer.data, 60*5)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Get Product Performance",parameters=[ProductPerformanceFilterSerializer],responses={200: ProductPerformanceSerializer})
    @action(detail=False, methods=["get"], url_path="performance")
    def product_performance(self, request):
        cache_key = make_cache_key(request, "analytics","product_performance", request.user)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data,status=status.HTTP_200_OK)

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
        cache.set(cache_key, serializer.data, 60*5)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="performance/report")
    def product_performance_report(self, request):
        cache_key = make_cache_key(request, "analytics","product_performance_report", request.user)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data,status=status.HTTP_200_OK)
        invoice_qs = Invoice.objects.filter(
            business=request.user.business
        )

        filterset = MonthlySummaryCreatedAtRangeFilter(
            request.GET,
            queryset=invoice_qs
        )

        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        if not filterset.qs.exists():
            return Response({"error": "Data not found"}, status=400)

        items_qs = ProductInvoice.objects.filter(
            invoice__in=filterset.qs
        )

        product_wise = (
            items_qs
            .annotate(
                product_name=F("product__name"),
                category_name=F("product__product_category__name"),
            )
            .values(
                "product_id",
                "product_name",
                "category_name",
            )
            .annotate(
                total_quantity_sold=Sum("quantity"),
                total_revenue=Sum(F("quantity") * F("selling_price")),
                total_profit=Sum(F("quantity") * F("product__net_profit")),
                total_cost=Sum(F("quantity") * F("product__cost_price")),
            )
        )

        summary = items_qs.aggregate(
            total_quantity_sold=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("selling_price")),
            total_profit=Sum(F("quantity") * F("product__net_profit")),
            total_cost=Sum(F("quantity") * F("product__cost_price")),
        )
        data={"summary": summary,"products": product_wise}
        cache.set(cache_key, data, 60*5)
        return Response(
            data,
            status=status.HTTP_200_OK
        )

