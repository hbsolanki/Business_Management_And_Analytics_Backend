from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.core.cache import cache

from apps.chat.models import Conversation, Message
from apps.chat.serializers.message import MessageSerializer
from apps.chat.pagination import MessageCursorPagination
from apps.core.cache import make_cache_key
from apps.chat.permission import ChatFeaturePermission


class MessagesViewSet(ModelViewSet):
    permission_classes = [ChatFeaturePermission]
    pagination_class = MessageCursorPagination
    queryset = Message.objects.none()

    def get_serializer_class(self):
        if self.action == "by_conversation":
            return MessageSerializer
        return MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,is_updated=True)

    def perform_destroy(self, instance):
        # instance.is_deleted = True
        # instance.is_active = False
        instance.deleted_text=instance.text
        instance.text=None
        instance.save(update_fields=["deleted_text","text"])

    def create(self, request, *args, **kwargs):
        return Response({"error": "Message creation Not Allow"},status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"],url_path=r"conversation/(?P<conversation_id>\d+)")
    def by_conversation(self, request, conversation_id=None):
        cache_key = make_cache_key(request,"chat",f":conversation:{conversation_id}",request.user)
        cache_data = cache.get(cache_key)
        if cache_data:
            return Response(cache_data,status=status.HTTP_200_OK)
        conversation = Conversation.objects.filter(
            id=conversation_id
        ).filter(
            Q(user1=request.user) | Q(user2=request.user)
        ).first()

        if not conversation:
            raise PermissionDenied("Not part of this conversation")

        messages_qs = (
            Message.objects
            .filter(conversation=conversation)
            .select_related("sender")
            # .order_by("-created_at")  # MUST match pagination ordering
        )

        page = self.paginate_queryset(messages_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response=self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60 * 2)
            return response

        serializer = self.get_serializer(messages_qs, many=True)
        cache.set(cache_key, serializer.data, timeout=60*2)
        return Response(serializer.data)


    @action(detail=False, methods=["post"],url_path=r"upload")
    def message_upload(self, request, conversation_id=None):
        return Response({"message":"uploaded"},status=status.HTTP_200_OK)

