from django.urls import path,include
from apps.chat.views import conversation,messages,broadcast
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("message", messages.MessagesViewSet, basename="messages")
router.register("broadcast", broadcast.BroadcastViewSet, basename="broadcast")
router.register("conversation",conversation.ConversationViewSet, basename="conversation")

urlpatterns = [
    path('', include(router.urls)),
]
