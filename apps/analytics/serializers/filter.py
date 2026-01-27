from rest_framework import serializers

class MonthYearFilterSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12, help_text="Month number (1-12)")
    year = serializers.IntegerField(min_value=2000, help_text="Year (e.g. 2025)")

class ProductPerformanceFilterSerializer(serializers.Serializer):
    product_id=serializers.IntegerField(required=False)
    from_date_and_time=serializers.DateTimeField()
    to_date_and_time=serializers.DateTimeField()