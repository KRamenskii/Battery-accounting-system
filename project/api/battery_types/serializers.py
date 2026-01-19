from rest_framework import serializers
from django.utils.html import escape
from battery_types.models import BatteryType


class BatteryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryType
        fields = [
            'id',
            'manufacturer',
            'battery_type_title',
            'nominal_voltage',
            'elements_count',
            'lifespan',
            'nominal_capacity_20',
            'nominal_capacity_10',
            'nominal_capacity_5',
            'self_discharge',
            'internal_resistance',
            'weight',
        ]
        read_only_fields = ['id']

    def validate_manufacturer(self, value):
        if not value.strip():
            raise serializers.ValidationError('Наименование производителя не может быть пустым')
        return escape(value.strip())
    
    def validate_battery_type_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Наименование типа АБ не может быть пустым')
        return escape(value.strip())
    
    def validate_nominal_voltage(self, value):
        if value <= 0:
            raise serializers.ValidationError('Номинальное напряжение не может быть пустым')
        return value
    
    def validate_elements_count(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество элементов АБ не может быть пустым')
        return value
    
    def validate_lifespan(self, value):
        if value <= 0:
            raise serializers.ValidationError('Срок службы не может быть пустым')
        return value
    
    def validate_nominal_capacity_20(self, value):
        if value <= 0:
            raise serializers.ValidationError('Номинальная емкость не может быть пустой')
        return value
    
    def validate_nominal_capacity_10(self, value):
        if value < 0:
            raise serializers.ValidationError('Номинальная емкость не может быть пустой')
        return value
    
    def validate_nominal_capacity_5(self, value):
        if value < 0:
            raise serializers.ValidationError('Номинальная емкость не может быть пустой')
        return value
    
    def validate_self_discharge(self, value):
        if value <= 0:
            raise serializers.ValidationError('Процент саморазряда не может быть пустым')
        return value
    
    def validate_internal_resistance(self, value):
        if value <= 0:
            raise serializers.ValidationError('Внутреннее сопротивление не может быть пустым')
        return value
    
    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError('Вес АБ не может быть пустым')
        return value