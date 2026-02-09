from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from apps.subscription.models import Subscription

def require_feature(business, feature):
    subscription = Subscription.objects.filter(business_id=business, feature=feature).first()
    if not subscription:
        raise PermissionDenied("subscription not found")
    if subscription.end_date < timezone.now():
        raise PermissionDenied("subscription expired")

    plan=subscription.plan
    if not getattr(plan, feature):
        raise PermissionDenied(f"{feature} not available in your plan")