from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [

    path('admin/', admin.site.urls),
    path('business/',include('apps.business.urls')),
    path('user/',include('apps.user.urls')),
    path('product/',include('apps.product.urls')),
    path('inventory/',include('apps.inventory.urls')),
    path('customer/',include('apps.customer.urls')),
    path('invoice/',include('apps.invoice.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('cost/', include('apps.cost.urls')),
    path('chat/',include('apps.chat.urls')),
    path('task/',include('apps.tasks.urls')),
    path('notification/',include('apps.notification.urls')),
    path('subscription/',include('apps.subscription.urls')),

    #urls
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    #  UI:
    path('api/schema-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    # serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # serve uploaded media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


