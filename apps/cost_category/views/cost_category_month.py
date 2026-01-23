from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.user.permission import IsOwnerOrManager
from apps.cost_category.services.monthly_cost_category import monthly_cost_category_create
from apps.cost_category.models import MonthlyCostCategory,MonthlyFinancialSummary
from apps.cost_category.serializers.cost_category_month import MonthlyAllCostCategoryCreateSerializer,MonthlyCostCategoryUpdateSerializer,MonthlyCostCategoryReadSerializer
from rest_framework.exceptions import ValidationError
from datetime import datetime


class MonthlyCostCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrManager]

    def get_month_summary(self):
        today = datetime.today()
        try:
            return MonthlyFinancialSummary.objects.get(business=self.request.user.business,year=today.year,month=today.month)
        except MonthlyFinancialSummary.DoesNotExist:
            raise ValidationError("Inventory not found")


    def get_queryset(self):
        return MonthlyCostCategory.objects.filter(monthly_summary=self.get_month_summary())

    def get_serializer_class(self):
        if self.action == "create":
            return MonthlyAllCostCategoryCreateSerializer
        if self.action == "monthly_cost_category_detail_update":
            return MonthlyCostCategoryUpdateSerializer
        return MonthlyCostCategoryReadSerializer



    def create(self, request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data["cost_category_items"]

        monthly_cost_category_create(cost_category_items=data, user=self.request.user)
        return  Response({"message":"successfully cost added"},status=status.HTTP_200_OK)
