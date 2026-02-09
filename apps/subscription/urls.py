from rest_framework.routers import DefaultRouter
from apps.subscription.views.subscription_plan import SubscriptionPlanViewSet
from apps.subscription.views.strip_payment import PaymentViewSet

router = DefaultRouter()
router.register(r'payment', PaymentViewSet, basename='payment')
router.register('', SubscriptionPlanViewSet, basename='subscription_plan')

urlpatterns = router.urls