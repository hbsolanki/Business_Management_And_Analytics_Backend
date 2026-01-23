
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.analytics.filters import MonthlySummaryMonthYearFilter
from apps.analytics.serializers.month_financial import MonthFinancialBreakdownSerializer
from apps.analytics.serializers.filter import MonthYearFilterSerializer
from apps.cost_month.models import MonthlyFinancialSummary
from apps.user.permission import IsOwnerOrManager
from drf_spectacular.utils import extend_schema

class MonthFinancialSummaryViewSet(GenericViewSet):
    permission_classes = [IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == "month_breakdown":
            return MonthFinancialBreakdownSerializer

        return None

    def get_queryset(self):
        return MonthlyFinancialSummary.objects.filter(
            business=self.request.user.business
        )

    @extend_schema(
        summary="Get Month Breakdown",
        parameters=[MonthYearFilterSerializer],
        responses={200: MonthFinancialBreakdownSerializer}
    )
    @action(detail=False, methods=["get"], url_path="breakdown")
    def month_breakdown(self, request):
        qs = self.get_queryset()

        filtered_set = MonthlySummaryMonthYearFilter(request.GET, queryset=qs)
        instance = filtered_set.qs.first()

        if not instance:
            return Response(
                {"detail": "Data not found for given month and year"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="netprofit")
    def month_net_profit(self, request):
        queryset = self.get_queryset()
        filter_instance = MonthlySummaryMonthYearFilter(request.GET, queryset=queryset)

        # Access the filtered queryset via .qs
        filtered_queryset = filter_instance.qs

        if not filtered_queryset.exists():
            return Response({"detail": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

        result = filtered_queryset.values_list('net_profit_after_tax', flat=True)

        return Response(list(result), status=status.HTTP_200_OK)

