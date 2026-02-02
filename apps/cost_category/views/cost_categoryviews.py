from rest_framework import viewsets

from apps.cost_category.models import CostCategory
from apps.cost_category.serializers.cost_category import CostCategorySerializer
from apps.user.permission import IsOwnerOrManager


class CostCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrManager]
    serializer_class = CostCategorySerializer

    def get_queryset(self):
        return CostCategory.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,business=self.request.user.business)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)