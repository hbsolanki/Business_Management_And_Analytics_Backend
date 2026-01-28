from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from apps.user.permission import IsOwner,IsOwnerOrManager,CanModifyUser,CanDeleteUser
from rest_framework.permissions import IsAuthenticated
from apps.user.services.user_service import  create_user,create_manager_employee
from apps.user.serializers import  create,read,update
from apps.user.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
import random


class UserViewSet(ModelViewSet):

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [CanModifyUser()]
        if self.action in ["destroy", "delete"]:
            return [CanDeleteUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'partial_update':
            if self.request.user.role == User.Role.OWNER:
                return update.OwnerUpdateSerializer
            return update.UserUpdateSerializer
        if self.request.user.role == User.Role.OWNER:
            return read.OwnerUserReadSerializer
        return read.UserReadSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in {User.Role.OWNER, User.Role.MANAGER}:
            return User.objects.filter(business=user.business)

        return User.objects.filter(id=user.id)

    def retrieve(self, request,pk):
        cache_key=f"user:{pk}"
        user=cache.get(cache_key)
        try:
            if not user:
                user=self.get_serializer(User.objects.get(pk=pk)).data
                cache.set(cache_key,user,timeout=80+int(random.random()*30))
            return Response(user, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error":"user not found"},status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
