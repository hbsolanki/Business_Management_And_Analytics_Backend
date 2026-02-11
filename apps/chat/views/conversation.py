from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from apps.chat.models import Conversation
from apps.user.models import User
from apps.chat.serializers.conversation import (ConversationGetOrCreateSerializer,
                                                ConversationBulkIdsSerializer,
                                                ConversationReadSerializer)
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from apps.chat.pagination import ChatCursorPagination
from rest_framework.decorators import action
from django.core.cache import cache
from apps.base.utils.cache import make_cache_key
from apps.base.permission.model_permissions import ModelPermissions


class ConversationViewSet(ModelViewSet):
    http_method_names = ["get", "post","delete"]
    permission_classes = [ModelPermissions]
    pagination_class = ChatCursorPagination

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(user1=user) | Q(user2=user))
            .select_related("user1", "user2")
        )


    def get_serializer_class(self):
        if self.action=="create":
            return ConversationGetOrCreateSerializer
        elif self.action=="bulk_delete":
            return ConversationBulkIdsSerializer

        return ConversationReadSerializer

    def list(self,request):
        cache_key=make_cache_key(request,"chat","conversation_list",request.user)
        cache_data=cache.get(cache_key)
        if cache_data:
            return Response(cache_data)
        queryset = self.get_queryset().order_by("-updated_at","-id")

        page_data=self.paginate_queryset(queryset)
        if page_data is not None:
            serializer = self.get_serializer(page_data,many=True)
            response=self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=20)
            return response

        serializer=self.get_serializer(queryset,many=True)
        cache.set(cache_key, serializer.data, timeout=20)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Create or get conversation",request=ConversationGetOrCreateSerializer,)
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation=serializer.save()
        return Response({"conversation_id": conversation.id },status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted","is_active"])

    @action(detail=False, methods=["post"],url_path="bulk-delete",url_name="bulk-delete")
    @transaction.atomic
    def bulk_delete(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.data

        return Response(data,status=status.HTTP_200_OK)
