from rest_framework import serializers


class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, data):
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError(
                    {"date_range": "start_date must be <= end_date"}
                )
        return data


class DateTimeRangeSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField(required=False)
    end_datetime = serializers.DateTimeField(required=False)

    def validate(self, data):
        if data.get("start_datetime") and data.get("end_datetime"):
            if data["start_datetime"] > data["end_datetime"]:
                raise serializers.ValidationError(
                    {"datetime_range": "start_datetime must be <= end_datetime"}
                )
        return data



class CustomerFilterSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False)
    mobile_number = serializers.CharField(required=False)


class ProductFilterSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)


class MonthYearFilterSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12,required=False)
    year = serializers.IntegerField(min_value=2000,required=False)


class CustomerInvoiceFilterSerializer(DateRangeSerializer, CustomerFilterSerializer):
    pass


class CustomerInvoiceProductFilterSerializer(DateRangeSerializer, CustomerFilterSerializer, ProductFilterSerializer):
    pass


class ProductPerformanceFilterSerializer(DateTimeRangeSerializer, ProductFilterSerializer):
    pass
