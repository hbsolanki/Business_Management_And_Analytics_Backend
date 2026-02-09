from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import  GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from apps.subscription.models import Plan, Subscription,Usage
from drf_spectacular.utils import extend_schema
from apps.subscription.serializers import plan,subsription
from datetime import timedelta
from django.utils import timezone

from apps.user.permission import IsOwnerOrManager


class SubscriptionPlanViewSet(GenericViewSet):

    def get_queryset(self):
        return Plan.objects.all()

    def get_serializer_class(self):
        if self.action == 'plan_purchase':
            return subsription.SubscriptionCreateSerializer
        elif self.action == 'purchased_plan':
            return subsription.SubscriptionReadSerializer
        elif self.action == 'plan_usage':
            return subsription.PlanUsageSerializer

        return plan.PlanReadSerializer

    def get_permissions(self):
        if self.action == "plans_details":
            return [AllowAny()]
        if self.action in ["plan_purchase", "purchased_plan"]:
            return [IsOwnerOrManager()]
        return super().get_permissions()

    @extend_schema(summary="Plan Details")
    @action(detail=False, methods=['get'], url_path="plan")
    def plans_details(self,request):
        print("details")
        serializer = self.get_serializer(Plan.objects.all(),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Purchase Plan")
    @action(detail=False, methods=['post'],url_path="plan/purchase")
    def plan_purchase(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # if Subscription.objects.filter(business=request.user.business,plan_id=serializer.validated_data['plan_id']).exists():
        #     return Response({"You have already purchased this plan"},status=status.HTTP_400_BAD_REQUEST)

        data=serializer.validated_data
        plan=Plan.objects.filter(id=data["plan_id"]).first()
        if not plan:
            return Response({"message": "Plan does not exist"},status=status.HTTP_400_BAD_REQUEST)

        now=timezone.now()
        end_date = now + timedelta(days=plan.duration_days)
        subscription=Subscription.objects.create(
            business=request.user.business,
            plan=plan,

            plan_name=plan.name,
            price=plan.price,
            duration_days=plan.duration_days,

            max_products=plan.max_products,
            max_invoices=plan.max_invoices,
            max_staff=plan.max_staff,

            has_advanced_analytics=plan.has_advanced_analytics,
            has_chat=plan.has_chat,
            has_api_access=plan.has_api_access,

            start_date=now,
            end_date=end_date
        )
        Usage.objects.create(
            subscription=subscription,
        )

        return Response({"message": "Plan activated successfully","plan": plan.name,"valid_till": end_date,}, status=status.HTTP_200_OK )

    @extend_schema(summary="Purchased Plan")
    @action(detail=False, methods=['get'],url_path="plan/purchased",permission_classes=[IsOwnerOrManager])
    def purchased_plan(self,request):
        data=Subscription.objects.filter(business=request.user.business).first()
        if not data:
            return Response({"message": "You not purchased any plan"},status=status.HTTP_400_BAD_REQUEST)

        serializer=self.get_serializer(data)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Plan Usage")
    @action(detail=True, methods=['get'], url_path="usage", permission_classes=[IsOwnerOrManager])
    def plan_usage(self, request,pk):
        try:
            subscription=Subscription.objects.get(id=pk ,business=request.user.business)
            usage_data=Usage.objects.filter(subscription=subscription).first()
            if not usage_data:
                return Response({"details": "Subscription Usage does not exist"},status=status.HTTP_400_BAD_REQUEST)

            serializer=self.get_serializer(usage_data)
            return Response(serializer.data,status=status.HTTP_200_OK)

        except Subscription.DoesNotExist:
            return Response({"details": "Subscription does not exist"},status=status.HTTP_400_BAD_REQUEST)






