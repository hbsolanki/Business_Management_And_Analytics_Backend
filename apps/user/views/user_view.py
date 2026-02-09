from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from apps.user.filters import UserFilter
from apps.user.permission import IsOwner,IsOwnerOrManager,CanModifyUser,CanDeleteUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.user.services.user_service import  create_user,create_manager_employee
from apps.user.serializers import  create,read,update
from apps.user.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
import random
from apps.core.pagination import CursorPagination
from apps.business.serializers import BusinessUserSerializer


class UserViewSet(ModelViewSet):
    pagination_class = CursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    search_fields = ["username"]

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [CanModifyUser()]
        if self.action in ["destroy", "delete"]:
            return [CanDeleteUser()]
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return create.OwnerCreateSerializer
        if self.action == 'partial_update':
            if self.request.user.role == User.Role.OWNER:
                return update.OwnerUpdateSerializer
            return update.UserUpdateSerializer
        if self.request.user.role == User.Role.OWNER:
            return read.OwnerUserReadSerializer
        if self.action=="search":
            return BusinessUserSerializer
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

    def perform_create(self, serializer):
        serializer.save(role=User.Role.Owner)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


    @action(detail=False, methods=["GET"],permission_classes=[IsAuthenticated])
    def search(self, request):
        queryset = User.objects.filter(business=request.user.business,is_active=True)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BusinessUserSerializer(queryset, many=True)
        return Response(serializer.data)