from rest_framework.routers import DefaultRouter
from apps.analytics.views import product_view,month_financial_summary
from django.urls import path,include


router = DefaultRouter()
router.register("product", product_view.AnalysisProductViewSet, basename="analysis")
router.register("month",month_financial_summary.MonthFinancialSummaryViewSet, basename="month_financial_summary")


# urlpatterns = router.urls

urlpatterns=[
    # path("insight/",insight_view.InsightAPIView.as_view(),name="insight"),
    path("",include(router.urls)),
]