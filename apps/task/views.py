from datetime import timezone

from rest_framework import viewsets, permissions, status
from apps.task.models import Task
from apps.task.serializers import TaskCreateSerializer,TaskReadSerializer,TaskUpdateSerializer
from apps.user.models import User
from rest_framework.response import Response
from rest_framework.decorators import action

class TaskViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','patch','delete']
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        return Task.objects.filter(business=user.business,assignee=user)

    def get_serializer_class(self):
        if self.action=='create':
            return TaskCreateSerializer
        elif self.action=='partial_update':
            return  TaskUpdateSerializer

        return TaskReadSerializer


    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        assignee=User.objects.filter(id=data["assignee_id"]).first()
        task=Task.objects.create(business=request.user.business,assignee=assignee,assigned_by=request.user,title=data["title"],description=data["description"])

        return Response({"assignee":assignee.username,"task_id":task.id},status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'],url_path='complate')
    def mark_complate(self, request,pk):
        task=Task.objects.get(id=pk)
        task.completed_at=timezone.now()
        task.save(update_fields=["completed_at"])
        return Response({"details":"task complated"},status=status.HTTP_200_OK)