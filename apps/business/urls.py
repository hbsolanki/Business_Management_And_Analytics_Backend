from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.business.views import BusinessViewSet

router = DefaultRouter()
router.register(r'', BusinessViewSet, basename='business')

urlpatterns = [
    path('', include(router.urls)),
]