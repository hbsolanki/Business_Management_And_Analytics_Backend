from rest_framework import viewsets
from apps.cost_month.serializers import MonthlyFinancialSummaryDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MonthCostFilter
from apps.core.pagination import CursorPagination
from apps.cost_month.models import MonthlyFinancialSummary
from apps.user.permission import IsOwnerOrManager


class CostMonthViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrManager]
    serializer_class = MonthlyFinancialSummaryDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class=MonthCostFilter
    pagination_class = CursorPagination

    def get_queryset(self):
        user=self.request.user
        return MonthlyFinancialSummary.objects.filter(business=user.business)
