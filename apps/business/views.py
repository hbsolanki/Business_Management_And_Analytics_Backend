from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.base.permission.model_permissions import ModelPermissions
from apps.user.models import User
from apps.business.models import Business
from apps.business.serializers import BusinesSerializer
from apps.user.serializers.user import UserSerializer,ManagerCreateSerializer,EmployeeCreateSerializer
from apps.user.utils.group_permission import sync_user_work_group


class BusinessViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [ModelPermissions]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business.id)

    def get_serializer_class(self):
        if self.action == "manager":
            if self.request.method == "GET":
                return UserSerializer
            return ManagerCreateSerializer

        if self.action == "employee":
            if self.request.method == "GET":
                return UserSerializer
            return EmployeeCreateSerializer

        return BusinesSerializer

    def perform_create(self, serializer):
        business=serializer.save(created_by=self.request.user)
        user=self.request.user
        user.business =business
        user.save()


    @action(detail=False,methods=["GET", "POST"],url_path="manager")
    def manager(self, request):
        if request.method == "GET":
            managers = User.objects.filter(business=request.user.business,role=User.Role.MANAGER,)
            serializer =self.get_serializer(managers, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save(created_by=self.request.user)

        return Response({"message": "Manager created successfully",},status=status.HTTP_201_CREATED,)

    @action(detail=False,methods=["GET", "POST"],url_path="employee",)
    def employee(self, request):
        if request.method == "GET":
            employees = User.objects.filter(business=request.user.business,role=User.Role.EMPLOYEE,)
            serializer = self.get_serializer(employees, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save(created_by=self.request.user)
        sync_user_work_group(user)

        return Response({"message": "Employee created successfully"}, status=status.HTTP_201_CREATED)
