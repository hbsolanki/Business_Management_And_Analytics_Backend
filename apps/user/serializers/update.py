from .base import BaseUserUpdateSerializer


class UserUpdateSerializer(BaseUserUpdateSerializer):
    pass

class OwnerUpdateSerializer(BaseUserUpdateSerializer):
    class Meta(BaseUserUpdateSerializer.Meta):
        fields = BaseUserUpdateSerializer.Meta.fields + ["role"]
