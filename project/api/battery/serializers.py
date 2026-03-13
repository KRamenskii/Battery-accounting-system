from rest_framework import serializers
from django.utils.html import escape
from journal.models import Battery
from api.serial_parameters.serializers import SerialParametersSerializer

class BatterySerializer(serializers.ModelSerializer):
    serial_parameters_detail = SerialParametersSerializer(
        source='serial_parameters', 
        read_only=True
    )

    class Meta:
        model = Battery
        fields = [
            'id', 
            'battery_type', 
            'serial_parameters', 
            'serial_parameters_detail', 
            'battery_number', 
            'acceptance_date', 
            'qr_code', 
            'qr_data_hash'
        ]
        read_only_fields = ['id', 'qr_code', 'qr_data_hash']
    
    def validate_battery_number(self, value):
        """Валидация номера АБ"""
        if value is not None:
            try:
                val = int(value)
                if val < 0:
                    raise serializers.ValidationError('Номер АБ не может быть отрицательным')
                return val
            except (TypeError, ValueError):
                raise serializers.ValidationError('Номер АБ должен быть целым числом')
        return value