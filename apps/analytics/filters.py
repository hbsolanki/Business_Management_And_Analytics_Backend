import django_filters
from apps.cost_category.models import MonthlyFinancialSummary
from apps.cost_month.models import MonthlyProductPerformance

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
