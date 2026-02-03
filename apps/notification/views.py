from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from apps.notification.models import Notification
from apps.notification.serializers import NotificationReadSerializer, NotificationBulkReadSerializer

class NotificationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationReadSerializer
    http_method_names = ['post','get','delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(methods=["post"], detail=True, url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(
            {"detail": "Notification marked as read"},
            status=status.HTTP_200_OK
        )

    @action(methods=["post"], detail=False, url_path="bulk-mark-read")
    def bulk_mark_read(self, request):
        serializer = NotificationBulkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"]

        Notification.objects.filter(
            id__in=ids,
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {"detail": "Notifications marked as read"},
            status=status.HTTP_200_OK
        )









