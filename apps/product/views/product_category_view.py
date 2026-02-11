from django.core.cache import cache
from rest_framework import viewsets
from apps.base.permission.model_permissions import ModelPermissions
from apps.product.models import ProductCategory
from apps.product.serializers.product_category import ProductCategorySerializer



class ProductCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ModelPermissions]
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        business=self.request.user.business
        cache_key=f"business:{business.id}:product_category"
        data=cache.get(cache_key)
        if data:
            return data
        data=ProductCategory.objects.filter(business=business)
        cache.set(cache_key,data,timeout=60*2)
        return data

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,business=self.request.user.business)

    def perform_update(self, serializer):
        business = self.request.user.business
        cache_key = f"business:{business.id}:product_category"
        serializer.save(updated_by=self.request.user)
        cache.delete(cache_key)

    def perform_destroy(self, instance):
        business=self.request.user.business
        cache_key=f"business:{business.id}:product_category"
        instance.delete()
        cache.delete(cache_key)
