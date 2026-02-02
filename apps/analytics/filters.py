import django_filters
from apps.cost_category.models import MonthlyFinancialSummary
from apps.cost_month.models import MonthlyProductPerformance
from apps.invoice.models import Invoice


class MonthlySummaryMonthYearFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(field_name="month",lookup_expr="exact")
    year = django_filters.NumberFilter(field_name="year",lookup_expr="exact")

    class Meta:
        model = MonthlyFinancialSummary
        fields = ["month", "year"]


class MonthlySummaryCreatedAtRangeFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte"
    )
    to_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte"
    )

    class Meta:
        model = MonthlyFinancialSummary
        fields = ["from_date", "to_date"]


class ProductPerformanceMonthYearFilter(django_filters.FilterSet):
    product_id = django_filters.NumberFilter(field_name="product_id",lookup_expr="exact")
    from_date = django_filters.DateFilter(
        field_name="monthly_summary__created_at",
        lookup_expr="date__gte"
    )
    to_date = django_filters.DateFilter(
        field_name="monthly_summary__created_at",
        lookup_expr="date__lte"
    )

    class Meta:
        model = MonthlyProductPerformance
        fields = ["product_id", "from_date", "to_date"]


class ProductPerformanceCreatedAtRangeFilter(django_filters.FilterSet):
    pass

class ProductPerformanceFilter(django_filters.FilterSet):
    product_id = django_filters.NumberFilter(field_name="invoice_items__product__id",lookup_expr="exact")
    from_date_and_time=django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte"
    )
    to_date_and_time=django_filters.DateTimeFilter(field_name="created_at",lookup_expr="lte")

    class Meta:
        model = Invoice
        fields = ["product_id","from_date_and_time", "to_date_and_time"]

#
# class ProductPerformanceFilter(django_filters.FilterSet):
#     product_id = django_filters.NumberFilter(field_name="product_invoice__product__id",lookup_expr="exact")
#     year = django_filters.NumberFilter(field_name="created_at__year", lookup_expr='exact')
#     month = django_filters.NumberFilter(field_name="created_at__month", lookup_expr='exact')
#     day = django_filters.NumberFilter(field_name="created_at__day", lookup_expr='exact')
#     hour = django_filters.NumberFilter(field_name="created_at__hour", lookup_expr='exact')
#     class Meta:
#         model = Invoice
#         fields = ["product_id", "year", "month", "day", "hour"]