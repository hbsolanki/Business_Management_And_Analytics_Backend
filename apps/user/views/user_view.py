from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,DjangoModelPermissions
from apps.user.filters import UserFilter
from django.db.models import Q
from apps.user.models import User
from rest_framework.response import Response
from django.core.cache import cache
import random
from apps.base.pagination import CursorPagination
from apps.user.serializers.user import UserSerializer,UserBasicDetailsSerializer,OwnerCreateSerializer
from apps.user.utils.group_permission import sync_user_work_group


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    search_fields = ["username"]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [DjangoModelPermissions()]

    def get_serializer_class(self):
        if self.action == "list":
            return UserBasicDetailsSerializer
        if self.action == "create":
            return OwnerCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = User.objects.filter(business=user.business)

        if user.role == User.Role.OWNER:
            return base_qs

        if user.role == User.Role.MANAGER:
            return base_qs.filter(
                Q(role=User.Role.EMPLOYEE) | Q(id=user.id)
            )

        return base_qs.filter(id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(User.objects.filter(business=request.user.business))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request,pk):
        cache_key=f"user:{pk}"
        user=cache.get(cache_key)
        try:
            if not user:
                user=self.get_serializer(self.get_object()).data
                # cache.set(cache_key,user,timeout=80+int(random.random()*30))
            return Response(user, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error":"user not found"},status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        request.data["role"]=User.Role.OWNER
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        user=serializer.save(updated_by=self.request.user)
        sync_user_work_group(user)
        cache.delete(f"user:{user.id}")


