from django.contrib import admin
from apps.cost_category.models import CostCategory,MonthlyCostCategory

admin.site.register(CostCategory)
admin.site.register(MonthlyCostCategory)