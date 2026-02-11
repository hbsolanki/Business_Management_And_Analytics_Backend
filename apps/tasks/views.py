from rest_framework import viewsets, status
from apps.base.permission.model_permissions import ModelPermissions
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from apps.tasks.filters import TaskFilter
from apps.tasks.utils.send_notification import send_notification
from django.core.cache import cache

class TaskViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','patch','delete']
    permission_classes=[ModelPermissions]
    filter_backends=[DjangoFilterBackend]
    filterset_class=TaskFilter

    def get_queryset(self):
        user = self.request.user
        cache_key = f"tasks:user:{user.id}"

        task_ids = cache.get(cache_key)

        if task_ids is None:
            task_ids = list(Task.objects.filter(business=user.business).filter(Q(assignee=user) | Q(assigned_by=user)).values_list("id", flat=True))
            cache.set(cache_key, task_ids, timeout=180)

        return Task.objects.filter(id__in=task_ids)

    def get_serializer_class(self):
        return TaskSerializer

    def retrieve(self, request, pk=None):
        user = request.user
        cache_key = f"tasks:{pk}"

        task = cache.get(cache_key)

        if task is None:
            task = get_object_or_404(Task,id=pk,business=user.business)

            # permission check
            if task.assignee != user and task.assigned_by != user:
                return Response({"detail": "Not allowed"},status=403)

            cache.set(cache_key, task, timeout=300)

        serializer = self.get_serializer(task )

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task=serializer.save()

        #notification
        send_notification(task,request)

        return Response({"assignee":task.assignee.username,"task_id":task.id},status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=kwargs["pk"])

        if request.user != task.assigned_by:
            return Response({"detail": "You do not have permission to delete this tasks."},status=status.HTTP_403_FORBIDDEN,)

        task.delete()

        return Response({"detail": "Task deleted successfully."},status=status.HTTP_200_OK,)

    @action(detail=False, methods=['get'],url_path='assigned_by')
    def task_assigned_by(self, request, *args, **kwargs):
        tasks=Task.objects.filter(assigned_by=request.user)
        serializer=self.get_serializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],url_path='assignee')
    def task_assignee(self, request, *args, **kwargs):
        user = self.request.user
        cache_key = f"tasks_assigned_by:user:{user.id}"

        tasks_ids = cache.get(cache_key)

        if tasks_ids is None:
            task_ids = list(
                Task.objects.filter(assigned_by=request.user)
                    .values_list("id", flat=True))
            cache.set(cache_key, task_ids, timeout=180)

        tasks=Task.objects.filter(id__in=tasks_ids)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],url_path='assignee')
    def task_assignee(self, request, *args, **kwargs):
        user = self.request.user
        cache_key = f"tasks_assignee:user:{user.id}"

        tasks_ids = cache.get(cache_key)

        if tasks_ids is None:
            task_ids = list(
                Task.objects.filter(assignee=request.user)
                .values_list("id", flat=True))
            cache.set(cache_key, task_ids, timeout=180)

        tasks = Task.objects.filter(id__in=tasks_ids)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
