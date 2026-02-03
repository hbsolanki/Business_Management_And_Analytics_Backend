from datetime import timezone

from rest_framework import viewsets, permissions, status
from apps.task.models import Task
from apps.task.serializers import TaskCreateSerializer,TaskReadSerializer,TaskUpdateSerializer
from apps.user.models import User
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from apps.task.filters import TaskFilter
from apps.task.services import send_notification

class TaskViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','patch','delete']
    permission_classes=[permissions.IsAuthenticated]
    filter_backends=[DjangoFilterBackend]
    filterset_class=TaskFilter

    def get_queryset(self):
        user=self.request.user
        return Task.objects.filter(business=user.business).filter(Q(assignee=user) | Q(assigned_by=user))

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

        #notification
        send_notification(task,request)

        return Response({"assignee":assignee.username,"task_id":task.id},status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs["pk"])

        if request.user != task.assigned_by:
            return Response({"detail": "You do not have permission to delete this task."},status=status.HTTP_403_FORBIDDEN,)

        task.delete()

        return Response({"detail": "Task deleted successfully."},status=status.HTTP_200_OK,)

    @action(detail=True, methods=['post'],url_path='complate')
    def mark_complate(self, request,pk):
        task=Task.objects.get(id=pk)
        task.completed_at=timezone.now()
        task.save(update_fields=["completed_at"])
        return Response({"details":"task complated"},status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],url_path='assigned_by')
    def task_assigned_by(self, request, *args, **kwargs):
        tasks=Task.objects.filter(assigned_by=request.user)
        serializer=TaskReadSerializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],url_path='assignee')
    def task_assignee(self, request, *args, **kwargs):
        tasks=Task.objects.filter(assignee=request.user)
        serializer=TaskReadSerializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
