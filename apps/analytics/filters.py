import django_filters
from apps.cost_category.models import MonthlyFinancialSummary
from apps.cost_month.models import MonthlyProductPerformance
from apps.invoice.models import Invoice,ProductInvoice
from datetime import datetime
import calendar


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

class CustomerCreatedAtRangeFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte"
    )
    to_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = Invoice
        fields = ["from_date", "to_date"]

class CustomerInvoiceFilter(django_filters.FilterSet):
    customer_id = django_filters.NumberFilter(field_name="customer__id")
    mobile_number = django_filters.CharFilter(
        field_name="customer__mobile_number",
        lookup_expr="exact"
    )

    from_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte"
    )

    to_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte"
    )

    class Meta:
        model = Invoice
        fields = ["customer_id","mobile_number", "from_date", "to_date"]


class CustomerInvoiceProductFilter(django_filters.FilterSet):
    customer_id = django_filters.NumberFilter(field_name="invoice__customer__id")
    product_id = django_filters.NumberFilter(field_name="product_id")
    mobile_number = django_filters.CharFilter(
        field_name="invoice__customer__mobile_number",
        lookup_expr="exact"
    )

    from_date = django_filters.DateFilter(
        field_name="invoice__created_at",
        lookup_expr="gte"
    )

    to_date = django_filters.DateFilter(
        field_name="invoice__created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = ProductInvoice
        fields = ["customer_id","product_id","mobile_number", "from_date", "to_date"]

class CustomerMonthYearFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(method="filter_month")
    year = django_filters.NumberFilter(method="filter_month")

    def filter_month(self, queryset, name, value):
        month = self.data.get("month")
        year = self.data.get("year")

        if not month or not year:
            return queryset

        month = int(month)
        year = int(year)

        last_day = calendar.monthrange(year, month)[1]

        start = datetime(year, month, 1, 0, 0, 0)
        end = datetime(year, month, last_day, 23, 59, 59)

        return queryset.filter(created_at__range=(start, end))

    class Meta:
        model = Invoice
        fields = ["month", "year"]

