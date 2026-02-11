from rest_framework import serializers
from apps.chat.models import BroadcastGroup,BroadcastGroupMember


class MessageBroadcastUserCreateSerializer(serializers.Serializer):
    user_id=serializers.IntegerField()

from rest_framework import serializers
from apps.chat.models import BroadcastGroup, BroadcastGroupMember
from apps.user.models import User


class BroadcastGroupMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    user_id = serializers.IntegerField(source="user_member_id", read_only=True)
    username = serializers.CharField(source="user_member.username", read_only=True)
    first_name = serializers.CharField(source="user_member.first_name", read_only=True)
    last_name = serializers.CharField(source="user_member.last_name", read_only=True)

    class Meta:
        model = BroadcastGroupMember
        fields = [
            "id",
            "user",
            "user_id",
            "username",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "user_id", "username", "first_name", "last_name"]


class BroadcastGroupSerializer(serializers.ModelSerializer):
    users = BroadcastGroupMemberSerializer(
        source="broadcast_group_members",
        many=True
    )

    class Meta:
        model = BroadcastGroup
        fields = ["id", "name", "users"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        users_data = validated_data.pop("broadcast_group_members", [])
        group = BroadcastGroup.objects.create(**validated_data)

        members = [
            BroadcastGroupMember(
                broadcast_group=group,
                user_member=item["user"]
            )
            for item in users_data
        ]

        BroadcastGroupMember.objects.bulk_create(members)
        return group
