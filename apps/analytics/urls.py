from rest_framework.routers import DefaultRouter
from apps.analytics.views import product_view,month_financial_summary,report,customer
from django.urls import path,include


router = DefaultRouter()
router.register("product", product_view.AnalysisProductViewSet, basename="analysis")
router.register("month",month_financial_summary.MonthFinancialSummaryViewSet, basename="month_financial_summary")
router.register("customer",customer.CustomerViewSet, basename="customer")


# urlpatterns = router.urls

urlpatterns=[
    path("",include(router.urls)),
]