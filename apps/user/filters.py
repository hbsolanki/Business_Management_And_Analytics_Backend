import django_filters
from django.db.models import Q
from apps.user.models import User


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = User
        fields = []  # we are using custom search only

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(role__icontains=value)
        )
