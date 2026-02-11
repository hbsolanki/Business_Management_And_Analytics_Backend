from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from apps.base.permission.model_permissions import ModelPermissions

from apps.cost.serializers.cost_month import MonthlyFinancialSummaryDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.cost.filters import MonthCostFilter
from apps.base.pagination import CursorPagination
from apps.cost.models import MonthlyFinancialSummary


class CostMonthViewSet(GenericViewSet,ListModelMixin):
    permission_classes = [ModelPermissions]
    serializer_class = MonthlyFinancialSummaryDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class=MonthCostFilter
    pagination_class = CursorPagination

    def get_queryset(self):
        user=self.request.user
        return MonthlyFinancialSummary.objects.filter(business=user.business)