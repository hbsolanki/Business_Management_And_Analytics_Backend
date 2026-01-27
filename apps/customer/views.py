from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.customer.models import Customer
from apps.customer.serializers import CustomerSerializer
from apps.customer.permission import CustomerPermission


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomerPermission]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(business=self.request.user.business)

    @action(methods=['get'], detail=False, url_path='mobile_number')
    def customer_get_by_mobile(self, request, *args, **kwargs):
        mobile_number = request.query_params.get("mobile_number")

        if not mobile_number:
            raise ValidationError({"detail": "Customer must have mobile_number"})

        try:
            customer = self.get_queryset().get(mobile_number=mobile_number)

            serializer = CustomerSerializer(customer)
            return Response(
                {"exists": True, "customer": serializer.data},
                status=status.HTTP_200_OK
            )

        except Customer.DoesNotExist:
            return Response(
                {"exists": False, "detail": "Customer does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )