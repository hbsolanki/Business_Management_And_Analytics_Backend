import django_filters
from apps.tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    title=django_filters.CharFilter(field_name='title',lookup_expr='icontains')
    from_date=django_filters.DateFilter(field_name='created_at',lookup_expr='gte')
    to_date=django_filters.DateFilter(field_name='created_at',lookup_expr='lte')
    remarks=django_filters.CharFilter(field_name='remarks',lookup_expr='icontains')
    class Meta:
        model = Task
        fields = ['title','from_date','to_date','remarks']
