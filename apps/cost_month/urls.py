from rest_framework import routers
from .views import CostMonthViewSet

router = routers.DefaultRouter()
router.register(r"", CostMonthViewSet, basename="cost_month")

urlpatterns = router.urls