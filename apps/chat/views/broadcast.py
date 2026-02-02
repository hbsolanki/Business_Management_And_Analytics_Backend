from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import transaction
from apps.chat.serializers.broadcast import BroadcastGroupCreateSerializer,BroadcastGroupReadSerializer,MessageBroadcastCreateSerializer
from apps.chat.models import BroadcastGroup,Conversation,Message,BroadcastGroupMember
from apps.user.models import User
from apps.user.permission import IsOwnerOrManager


class BroadcastViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        return BroadcastGroup.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return BroadcastGroupCreateSerializer
        if self.action == "message_broadcast":
            return MessageBroadcastCreateSerializer

        return BroadcastGroupReadSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        broadcast_group = BroadcastGroup.objects.create(user=request.user,name=data["name"])
        user_ids = {user["user_id"] for user in data["users"]}

        users = User.objects.filter(id__in=user_ids,business=self.request.user.business)
        if users.count() != len(user_ids):
            raise ValidationError("One or more users do not exist")

        members=[BroadcastGroupMember(broadcast_group=broadcast_group,user_member=user)for user in users]
        BroadcastGroupMember.objects.bulk_create(members)

        return Response({"message": "Broadcast Group created"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path=r"message", permission_classes=[IsOwnerOrManager])
    @transaction.atomic
    def message_broadcast(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        for user in data["users"]:
            user2 = User.objects.get(id=user["user_id"])
            user1 = request.user
            if user1.id > user2.id:
                user1, user2 = user2, user1

            conversation, created = Conversation.objects.get_or_create(user1=user1, user2=user2)

            Message.objects.create(conversation=conversation, sender=user1, text=data["message"])

        return Response({"message": "message broadcasted"}, status=status.HTTP_200_OK)
