from rest_framework import routers
from apps.cost.views import CostMonthViewSet, CostCategoryViewSet, MonthlyCostCategoryViewSet

router = routers.DefaultRouter()
router.register(r"category/month", MonthlyCostCategoryViewSet, basename="monthly-cost-category")
router.register(r"category", CostCategoryViewSet, basename="cost-category")
router.register(r"month", CostMonthViewSet, basename="cost")

urlpatterns = router.urls