from django import forms
from .models import BatteryType

class BatteryTypeForm(forms.ModelForm):
    class Meta:
        model = BatteryType
        fields = [
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
        ]