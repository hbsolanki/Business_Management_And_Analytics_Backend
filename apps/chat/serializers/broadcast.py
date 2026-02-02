from rest_framework import serializers

from apps.chat.models import BroadcastGroup,BroadcastGroupMember


class MessageBroadcastUserCreateSerializer(serializers.Serializer):
    user_id=serializers.IntegerField()

class MessageBroadcastCreateSerializer(serializers.Serializer):
    message = serializers.CharField()
    users = MessageBroadcastUserCreateSerializer(many=True)

class BroadcastGroupMemberCreateSerializer(serializers.Serializer):
    user_id=serializers.IntegerField()


class BroadcastGroupCreateSerializer(serializers.Serializer):
    name=serializers.CharField(required=True)
    users=BroadcastGroupMemberCreateSerializer(many=True)


class BroadcastGroupMemberReadSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(source="user_member_id",read_only=True)
    username = serializers.CharField(source="user_member.username", read_only=True)
    first_name = serializers.CharField(source="user_member.first_name", read_only=True)
    last_name = serializers.CharField(source="user_member.last_name", read_only=True)

    class Meta:
        model = BroadcastGroupMember
        fields = ["id", "user_id","username", "first_name", "last_name"]


class BroadcastGroupReadSerializer(serializers.ModelSerializer):
    users=BroadcastGroupMemberReadSerializer(source="broadcast_group_members",many=True,read_only=True)
    class Meta:
        model = BroadcastGroup
        fields=["id","name","users"]