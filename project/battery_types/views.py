from django.shortcuts import render
from .models import BatteryType

def battery_types_view(request):
    battery_types = BatteryType.objects.all()
    return render(request, 'battery_types/battery_types.html', {'battery_types': battery_types})