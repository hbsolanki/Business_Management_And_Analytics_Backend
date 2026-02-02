from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.task.views import TaskViewSet

router = DefaultRouter()
router.register('', TaskViewSet,basename='task')

urlpatterns =router.urls
