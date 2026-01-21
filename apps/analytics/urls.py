from rest_framework.routers import DefaultRouter
from apps.analytics.views import product_view,business_view,month_financial_summary

router = DefaultRouter()
router.register("product", product_view.AnalysisProductViewSet, basename="analysis")
router.register("month",month_financial_summary.MonthFinancialSummaryViewSet, basename="month_financial_summary")


urlpatterns = router.urls
