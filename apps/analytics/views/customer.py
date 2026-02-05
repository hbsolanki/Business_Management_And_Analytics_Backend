from django.db.models import Sum, F, Count, Avg, Max, Min,Q,DecimalField, ExpressionWrapper,Subquery,OuterRef
from django.db.models.functions import Round
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from apps.invoice.models import Invoice,ProductInvoice
from apps.user.permission import IsOwnerOrManager
from apps.analytics.filters import CustomerCreatedAtRangeFilter, CustomerInvoiceFilter,CustomerInvoiceProductFilter,CustomerMonthYearFilter
from apps.analytics.serializers.customer import (
    CustomerRevenueLeaderboardSerializer,
    CustomerRetentionAnalyticsSerializer,
    CustomerCreatedAtRangeSerializer,
    CustomerProductPreferenceSerializer,
    CustomerProductNestedSerializer,
    CustomerSpendSerializers
)
from apps.analytics.serializers.filter import CustomerInvoiceFilterSerializer, CustomerInvoiceProductFilterSerializer,MonthYearFilterSerializer
from drf_spectacular.utils import extend_schema
from apps.analytics.pagination import AnalyticsCustomerCursorPagination,DefaultPagination
from apps.analytics.utils import CURSOR_ORDERINGS
from django.core.cache import cache
from apps.core.cache import make_cache_key


class CustomerViewSet(GenericViewSet):
    permission_classes = [IsOwnerOrManager]

    def get_pagination_class(self):
        if self.action in CURSOR_ORDERINGS:
            ordering_tuple = CURSOR_ORDERINGS[self.action]

            return type(
                "ActionCursorPagination",
                (AnalyticsCustomerCursorPagination,),
                {"ordering": ordering_tuple},
            )

        if self.action in ["customer_product", "customer_spend"]:
            return DefaultPagination

        return None

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            pagination_class = self.get_pagination_class()
            self._paginator = pagination_class() if pagination_class else None
        return self._paginator


    def get_queryset(self):
        return Invoice.objects.filter(
            business=self.request.user.business
    )

    def get_filter_set(self):
        if self.action == "customer_leaderboard_revenue":
            return CustomerInvoiceFilter
        elif self.action == "customer_metrics_retention":
            return CustomerCreatedAtRangeFilter
        elif self.action == "customer_product_preference":
            return CustomerInvoiceFilter
        elif self.action == "customer_product":
            return CustomerInvoiceProductFilter
        elif self.action=="customer_spend":
            return CustomerMonthYearFilter
        return None

    def apply_filters(self, request, queryset):
        filterset_class = self.get_filter_set()
        if not filterset_class:
            return queryset, None

        filterset = filterset_class(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return None, Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        return filterset.qs, None

    @extend_schema(summary="Customer Leaderboard Revenue", parameters=[CustomerInvoiceFilterSerializer],responses={200: CustomerRevenueLeaderboardSerializer(many=True)})
    @action(methods=["get"],detail=False,url_path="leaderboard/revenue")
    def customer_leaderboard_revenue(self, request):
        cache_key = make_cache_key(request, "customer_leaderboard_revenue", request.user)

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        invoice_qs, error = self.apply_filters(request, self.get_queryset())
        if error:
            return error


        data = (
            invoice_qs
            .annotate(
                customer_name=F("customer__name"),
                customer_mobile_number=F("customer__mobile_number"),
            )
            .values(
                "customer_id",
                "customer_name",
                "customer_mobile_number",
            )
            .annotate(
                total_revenue=Sum("total_amount"),
                order_count=Count("id"),
                avg_order_value=Round(Avg("total_amount"), 2),
                first_order_at=Min("created_at"),
                last_order_at=Max("created_at"),
            )
            .order_by("-total_revenue","customer_id")
        )
        page_data = self.paginate_queryset(data)

        if page_data is not None:
            serializer = CustomerRevenueLeaderboardSerializer(page_data, many=True)
            response=self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 5)
            return response

        serializer = CustomerRevenueLeaderboardSerializer(data, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 5)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Customer Metrics Retention", parameters=[CustomerCreatedAtRangeSerializer],responses={200: CustomerRetentionAnalyticsSerializer})
    @action(methods=["get"], detail=False, url_path="metrics/retention")
    def customer_metrics_retention(self, request):
        cache_key = make_cache_key(request, "customer_metrics_retention", request.user)

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        invoice_qs, error = self.apply_filters(request, self.get_queryset())
        if error:
            return error


        customer_stats = (
            invoice_qs
            .values("customer_id")
            .annotate(order_count=Count("id"))
        )
        data=customer_stats.aggregate(
            total_customers=Count("customer_id",distinct=True),
            new_customers=Count("customer_id",filter=Q(order_count=1),distinct=True),
            returning_customers=Count("customer_id", filter=Q(order_count__gt=1), distinct=True),
        )
        total_customers = data["total_customers"] or 1
        data["retention_rate"] = round(data["returning_customers"] / total_customers * 100,2)
        data["churn_rate"] = round(100 - data["retention_rate"],2)
        serializer = CustomerRetentionAnalyticsSerializer(data)
        cache.set(cache_key, serializer.data, timeout=60 * 5)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Customer Product Preferences", parameters=[CustomerInvoiceFilterSerializer],responses={200: CustomerProductPreferenceSerializer(many=True)})
    @action(methods=["get"], detail=False, url_path="product/preferences")
    def customer_product_preference(self, request):
        cache_key = make_cache_key(request, "customer_product_preference", request.user)

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        invoice_qs, error = self.apply_filters(request, self.get_queryset())
        if error:
            return error

        if error:
            return Response({"detail": "No data found"}, status=status.HTTP_404_NOT_FOUND)

        products_invoice_qs = ProductInvoice.objects.filter(invoice__in=invoice_qs)
        # grouped totals
        customer_product_totals = (
            products_invoice_qs
            .values("invoice__customer__mobile_number", "product")
            .annotate(
                total_qty=Sum("quantity"),
                revenue=Sum(F("quantity") * F("selling_price"))
            )
        )
        # subquery from base table
        max_qty_subquery = (
            ProductInvoice.objects
            .filter(
                invoice__customer=OuterRef("invoice__customer"),
                invoice__in=invoice_qs
            )
            .values("invoice__customer", "product")
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")
            .values("total_qty")[:1]
        )

        #  match max quantity per customer
        product_preferences_data = (
            customer_product_totals
            .annotate(max_qty=Subquery(max_qty_subquery))
            .filter(total_qty=F("max_qty"))
            .values(
                customer_id=F("invoice__customer"),
                customer_name=F("invoice__customer__name"),
                product_id=F("product"),
                product_category=F("product__product_category__name"),
                product_name=F("product__name"),
                quantity=F("total_qty"),
                total_revenue=F("revenue"),
            )
            .order_by("total_revenue","customer_id")
        )


        page=self.paginate_queryset(product_preferences_data)
        if page is not None:
            serializer = CustomerProductPreferenceSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 5)
            return response

        serializer = CustomerProductPreferenceSerializer(product_preferences_data, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 5)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Customer Products", parameters=[CustomerInvoiceProductFilterSerializer],
                   responses={200: CustomerProductNestedSerializer(many=True)})
    @action(methods=["get"], detail=False, url_path="product")
    def customer_product(self, request):
        cache_key = make_cache_key(request, "customer_product", request.user)

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        products_invoice_qs, error = self.apply_filters(request, ProductInvoice.objects.filter(invoice__in=self.get_queryset()) )
        if error:
            return error


        # grouped totals
        customer_product_totals = (
            products_invoice_qs
            .values(
                customer_id=F("invoice__customer"),
                customer_name=F("invoice__customer__name"),
                mobile_number=F("invoice__customer__mobile_number"),

                p_id=F("product"),
                product_name=F("product__name"),
            )
            .annotate(
                quantity=Sum("quantity"),
                total_revenue=ExpressionWrapper(
                    F("quantity") * F("selling_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .order_by("invoice__customer__name")
        )
        grouped = {}

        for row in customer_product_totals:
            cid = row["customer_id"]

            if cid not in grouped:
                grouped[cid] = {
                    "customer_id": row["customer_id"],
                    "customer_name": row["customer_name"],
                    "mobile_number": row["mobile_number"],
                    "products": []
                }

            grouped[cid]["products"].append({
                "p_id": row["p_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "total_revenue": row["total_revenue"],
            })

        final_data = list(grouped.values())

        page=self.paginate_queryset(final_data)
        if page is not None:
            serializer = CustomerProductNestedSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 5)
            return response

        serializer = CustomerProductNestedSerializer(final_data, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 5)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Customer Spend-Trend", parameters=[MonthYearFilterSerializer],
                   responses={200: CustomerSpendSerializers(many=True)})
    @action(methods=["get"], detail=False, url_path="spend")
    def customer_spend(self, request):
        cache_key = make_cache_key(request, "customer_spend", request.user)

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        invoice_qs, error = self.apply_filters(request, self.get_queryset())
        if error:
            return error

        data = (
            invoice_qs
            .values(
                c_id=F("customer"),
                customer_name=F("customer__name"),
                mobile_number=F("customer__mobile_number"),
            )
            .annotate(
                total_revenue=Sum("total_amount")
            )
            .order_by("-total_revenue")
        )

        # response = self.get_paginated_response(data)
        cache.set(cache_key, data, timeout=60 * 5)
        return Response(data, status=status.HTTP_200_OK)
