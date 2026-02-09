from rest_framework.permissions import BasePermission
from apps.subscription.services.access import can_use_feature

class FeaturePermission(BasePermission):
    feature_name=None

    def has_permission(self,request,view):
        if not self.feature_name:
            return True

        allowed, message = can_use_feature(
            request.user.business,
            self.feature_name
        )

        if not allowed:
            self.message=message
            return False

        return True