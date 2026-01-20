from rest_framework import serializers
from apps.cost_category.models import MonthlyFinancialSummary


class MonthlyFinancialSummaryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyFinancialSummary
        fields = [
            "id",
            "year",
            "month",
            "revenue",
            "products_total_cost",
            "total_cost",
            "gross_profit",
            "net_profit_before_tax",
            "net_profit_after_tax",
            "taxes",
            "salary_expenditure",
            "input_gst",
            "output_gst",
            "gst_payable",
            "invoice_count",
        ]
        read_only_fields = fields
