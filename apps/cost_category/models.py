from apps.core.model import BaseModel
from apps.business.models import Business
from django.db import models
from apps.cost_month.models import MonthlyFinancialSummary


class CostCategory(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "bma_cost_category"
        indexes = [models.Index(fields=["business"])]


class MonthlyCostCategory(models.Model):
    cost_category = models.ForeignKey(CostCategory, on_delete=models.SET_NULL, null=True,blank=True)
    monthly_summary = models.ForeignKey(MonthlyFinancialSummary, on_delete=models.CASCADE, related_name="cost_category_items")
    cost=models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = "bma_monthly_cost_category"
        constraints = [
            models.UniqueConstraint(
                fields=["monthly_summary", "cost_category"],
                name="uniq_month_cost_category"
            )
        ]
        indexes = [
            models.Index(fields=["monthly_summary"])
        ]

