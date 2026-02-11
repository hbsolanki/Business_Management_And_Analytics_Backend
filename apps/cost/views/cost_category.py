from rest_framework import viewsets
from apps.base.permission.model_permissions import ModelPermissions

from apps.cost.models import CostCategory
from apps.cost.serializers.cost_category_month import CostCategorySerializer


class CostCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ModelPermissions]
    serializer_class = CostCategorySerializer
    http_method_names = ["get","post","patch","delete"]

    def get_queryset(self):
        return CostCategory.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,business=self.request.user.business)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
