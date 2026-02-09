from django.utils import timezone
from apps.subscription.models import Subscription,Usage

def get_active_subscription(business):
    now = timezone.now()

    return Subscription.objects.filter(
        business=business,
        start_date__lte=now,
        end_date__gte=now
    ).first()


def can_use_feature(business,feature_name,usage_field=None):
    subscription = get_active_subscription(business)

    if not subscription:
        return False,"No active subscription"

    #feature like chat,apis
    if usage_field is None:
        allow=getattr(subscription,feature_name)
        if not allow:
            return False,f"{feature_name} not allow in your plan"
        return True,True

    limit=getattr(subscription,feature_name)

    #for unlimited plan
    if limit is None:
        return True,True

    usage=Usage.objects.filter(subscription=subscription).first()

    if not usage:
        return  True,True

    current=getattr(usage,usage_field)
    if current>=limit:
        return False,f"{feature_name} limit reached"

    return True,True

