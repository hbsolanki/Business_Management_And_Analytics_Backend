import django_filters
from apps.cost.models import MonthlyFinancialSummary


class MonthCostFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte"
    )
    to_date = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte"
    )
    month = django_filters.NumberFilter(field_name="month")
    year = django_filters.NumberFilter(field_name="year")

    class Meta:
        model = MonthlyFinancialSummary
        fields = ["from_date", "to_date", "month", "year"]
