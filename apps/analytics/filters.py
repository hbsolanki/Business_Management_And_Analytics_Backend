import django_filters
from apps.cost_category.models import MonthlyFinancialSummary


class MonthCostFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(field_name="month")
    year = django_filters.NumberFilter(field_name="year")

    class Meta:
        model = MonthlyFinancialSummary
        fields = ["month", "year"]
