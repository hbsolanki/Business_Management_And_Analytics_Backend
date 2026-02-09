from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from apps.chat.models import Conversation
from apps.user.models import User
from apps.chat.serializers.conversation import (ConversationGetOrCreateSerializer,
                                                ConversationGetOrCreateResponseSerializer,
                                                ConversationReadSerializer,
                                                ConversationBulkIdsSerializer)
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from apps.chat.pagination import ConversationCursorPagination
from rest_framework.decorators import action
from django.core.cache import cache
from apps.core.cache import make_cache_key
from apps.chat.permission import ChatFeaturePermission


class ConversationViewSet(ModelViewSet):
    http_method_names = ["get", "post","delete"]
    permission_classes = [ChatFeaturePermission]
    serializer_class = ConversationGetOrCreateResponseSerializer
    pagination_class = ConversationCursorPagination

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(user1=user) | Q(user2=user))
            .select_related("user1", "user2")
        )


    def get_serializer_class(self):
        if self.action=="create":
            return ConversationGetOrCreateResponseSerializer
        if self.action=="bulk_delete":
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
            cache.set(cache_key, response.data, timeout=60)
            return response

        serializer=self.get_serializer(queryset,many=True)
        cache.set(cache_key, serializer.data, timeout=60)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(summary="Create or get conversation",request=ConversationGetOrCreateSerializer,responses={200: ConversationGetOrCreateResponseSerializer})
    def create(self, request):
        serializer = ConversationGetOrCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        other_user_id = serializer.validated_data["user_id"]

        if not other_user_id:
            return Response({"detail": "user_id required"},status=status.HTTP_400_BAD_REQUEST)

        if other_user_id == request.user.id:
            return Response({"detail": "Cannot chat with yourself"},status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"},status=status.HTTP_404_NOT_FOUND)

        user1, user2 = request.user, other_user
        if user1.id > user2.id:
            user1, user2 = user2, user1

        conversation, created = Conversation.objects.get_or_create(user1=user1,user2=user2)
        if created:
            conversation.created_by = request.user
            conversation.save(update_fields=["created_by"])

        return Response({"conversation_id": conversation.id,"created": created })

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted","is_active"])

    @action(detail=False, methods=["post"],url_path="bulk-delete",url_name="bulk-delete")
    @transaction.atomic
    def bulk_delete(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids=serializer.validated_data["ids"]

        if not ids:
            return Response({"detail": "ids required"},status=status.HTTP_400_BAD_REQUEST)
        user=request.user
        qs = Conversation.objects.filter(id__in=ids).filter(Q(user1=user) | Q(user2=user))

        if qs.count() != len(ids):
            return Response({"detail": "some ids not found or not allowed"},status=status.HTTP_400_BAD_REQUEST)

        qs.update(is_deleted=True,is_active=False)

        return Response({"detail": "conversations deleted"},status=status.HTTP_200_OK)
