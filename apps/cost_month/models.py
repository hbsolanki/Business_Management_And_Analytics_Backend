from django.db import models
from apps.core.model import BaseModel
from apps.business.models import Business
from apps.product.models import Product


class MonthlyFinancialSummary(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()

    revenue = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    products_total_cost = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    total_cost = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    net_profit_before_tax = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    net_profit_after_tax= models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    gross_profit=models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    taxes = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    salary_expenditure=models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    input_gst = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    output_gst = models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)
    gst_payable=models.DecimalField(default=0,max_digits=12, decimal_places=2,blank=True, null=True)

    invoice_count = models.PositiveIntegerField(default=0,blank=True, null=True)

    class Meta:
        db_table = "bma_monthly_financial_summary"
        constraints = [
            models.UniqueConstraint(
                fields=["business", "year", "month"],
                name="uniq_business_month_year"
            )
        ]
        indexes = [
            models.Index(fields=["business", "year", "month"])
        ]

class MonthlyProductPerformance(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,blank=True)
    monthly_summary = models.ForeignKey(MonthlyFinancialSummary, on_delete=models.CASCADE,related_name="product_performance")
    quantity = models.PositiveIntegerField()
    cost = models.DecimalField(default=0,max_digits=10, decimal_places=2)
    revenue = models.DecimalField(default=0,max_digits=10, decimal_places=2)

    class Meta:
        db_table = "bma_monthly_product_performance"
        constraints = [
            models.UniqueConstraint(
                fields=["monthly_summary", "product"],
                name="uniq_month_product"
            )
        ]
        indexes = [
            models.Index(fields=["monthly_summary"])
        ]







