from logging import raiseExceptions

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from apps.user.services.user_service import get_tokens_for_user, create_user,create_manager_employee
from apps.user.models import User
from apps.business.serializers import BusinessReadSerializer, BusinessCreateSerializer, OnwerBusinessReadSerializer,BusinessUserSerializer
from apps.business.models import Business
from apps.user.permission import IsOwner
from django.db import  transaction
from apps.inventory.services.inventory_service import create_inventory
from apps.user.permission import IsOwnerOrManager
from apps.user.serializers import create,read


class BusinessViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.action == "create":
            return BusinessCreateSerializer
        elif self.action == "business_users":
            return BusinessUserSerializer
        if self.request.user.role==User.Role.OWNER:
            return OnwerBusinessReadSerializer
        return BusinessReadSerializer

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business.id)

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action == "business_users":
            return [IsAuthenticated()]
        return [IsOwner()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            business = Business.objects.create(name=serializer.validated_data["name"],description=serializer.validated_data["description"])

            owner_user = create_user(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                username=serializer.validated_data['username'],
                mobile_number=serializer.validated_data['mobile_number'],
                password=serializer.validated_data['password'],
                role=User.Role.OWNER,
                business=business
            )
            create_inventory(business)
            token = get_tokens_for_user(owner_user)
            return Response({
                "business_id": business.id,
                "user":{
                    "id": owner_user.id,
                    "username": owner_user.username,
                    "role":owner_user.role,
                }
               ,"access": token["access"],
                "refresh": token["refresh"],
            },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error","something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET", "POST"],
        url_path="manager",
        permission_classes=[IsOwner],
    )
    def manager(self, request):

        if request.method == "GET":
            managers = User.objects.filter(
                business=request.user.business,
                role=User.Role.MANAGER,
            )
            serializer = read.UserReadSerializer(managers, many=True)
            return Response(serializer.data)

        serializer = create.ManagerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = create_manager_employee(
            **serializer.validated_data,
            business=request.user.business,
            user=request.user,
            role=User.Role.MANAGER,
        )

        return Response(
            {
                "message": "Manager created successfully",
                "manager": {
                    "id": manager.id,
                    "username": manager.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["GET", "POST"],
        url_path="employee",
        permission_classes=[IsOwnerOrManager],
    )
    def employee(self, request):

        if request.method == "GET":
            employees = User.objects.filter(
                business=request.user.business,
                role=User.Role.EMPLOYEE,
            )
            serializer = read.UserReadSerializer(employees, many=True)
            return Response(serializer.data)

        serializer = create.EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = create_manager_employee(
            **serializer.validated_data,
            business=request.user.business,
            user=request.user,
            role=User.Role.EMPLOYEE,
        )

        return Response(
            {
                "message": "Employee created successfully",
                "employee": {
                    "id": employee.id,
                    "username": employee.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )

