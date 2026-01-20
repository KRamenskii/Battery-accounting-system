from rest_framework import serializers
from django.utils.html import escape
from journal.models import SerialParameters
from battery_types.models import BatteryType
from api.battery_types.serializers import BatteryTypeSerializer

class SerialParametersSerializer(serializers.ModelSerializer):
    battery_type_detail = BatteryTypeSerializer(
        source='battery_type', 
        read_only=True
    )

    class Meta:
        model = SerialParameters
        fields = ['id', 'battery_type', 'battery_type_detail', 'serial_number', 'manufacture_date']
        read_only_fields = ['id', 'battery_type_detail']
    
    def validate_serial_number(self, value):
        if not value.strip():
            raise serializers.ValidationError('Серийный номер типа АБ не может быть пустой')
        return escape(value.strip())
    
    def validate_manufacture_date(self, value):
        from datetime import date

        if value is None:
            raise serializers.ValidationError('Дата производства не может быть пустой')

        if value > date.today():
            raise serializers.ValidationError('Дата производства не может быть в будущем')

        return value