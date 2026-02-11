from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.base.permission.model_permissions import ModelPermissions
from datetime import datetime

from apps.cost.models import MonthlyCostCategory
from apps.cost.serializers.cost_category_month import MonthlyAllCostCategoryCreateSerializer, MonthlyCostCategoryReadSerializer


class MonthlyCostCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ModelPermissions]
    http_method_names = ["get","post","patch","delete"]

    def get_queryset(self):
        today = datetime.today()
        return MonthlyCostCategory.objects.filter(
            monthly_summary__business=self.request.user.business,
            monthly_summary__year=today.year,
            monthly_summary__month=today.month
        )

    def get_serializer_class(self):
        if self.action=="create":
            return MonthlyAllCostCategoryCreateSerializer

        return MonthlyCostCategoryReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return  Response({"message":"successfully cost added"},status=status.HTTP_200_OK)
