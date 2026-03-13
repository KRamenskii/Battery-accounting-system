from rest_framework import serializers
from django.utils.html import escape
from journal.models import InstallationLocation

class InstallationLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallationLocation
        fields = ['id', 'location_title', 'location_type', 'system_title', 'system_name', 'nominal_capacity', 'battery_count', 'parent_location', 'nesting_level']
        read_only_fields = ['id']
    
    def validate_location_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Название места установки не может быть пустым!')
        return escape(value.strip())
    
    def validate_location_type(self, value):
        """Валидация типа места установки"""
        valid_types = ['container', 'virtual']
        
        if value not in valid_types:
            raise serializers.ValidationError(
                f'Недопустимый тип места установки. Допустимые значения: {", ".join(valid_types)}'
            )
        
        return value
    
    def validate_battery_count(self, value):
        """Валидация количества АБ"""
        if value is not None:
            try:
                val = int(value)
                if val < 0:
                    raise serializers.ValidationError('Количество АБ не может быть отрицательным')
                return val
            except (TypeError, ValueError):
                raise serializers.ValidationError('Количество АБ должно быть целым числом')
        return value
    
    def validate_nesting_level(self, value):
        """Валидация уровня вложенности"""
        if value is not None:
            try:
                val = int(value)
                if val < 0:
                    raise serializers.ValidationError('Количество АБ не может быть отрицательным')
                return val
            except (TypeError, ValueError):
                raise serializers.ValidationError('Количество АБ должно быть целым числом')
        return value