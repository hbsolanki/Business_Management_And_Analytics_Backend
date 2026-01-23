from rest_framework import serializers

class MonthYearFilterSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12, help_text="Month number (1-12)")
    year = serializers.IntegerField(min_value=2000, help_text="Year (e.g. 2025)")