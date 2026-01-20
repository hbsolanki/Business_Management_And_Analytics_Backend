from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from apps.analytics.serializers.month_financial import MonthFinancialBreakdonwSerializer

class MonthFinancialSummaryViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'],url_path='breakdown')
    def month_breakdown(self, request, pk=None):
        pass