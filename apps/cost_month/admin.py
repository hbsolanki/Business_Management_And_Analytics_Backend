from django.contrib import admin
from apps.cost_month.models import MonthlyFinancialSummary, MonthlyProductPerformance

admin.site.register(MonthlyFinancialSummary)
admin.site.register(MonthlyProductPerformance)

