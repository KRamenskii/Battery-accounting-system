from django.contrib import admin
from .models import BatteryType

@admin.register(BatteryType)
class BatteryTypeAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'battery_type_title', 'nominal_voltage', 'nominal_capacity_20')
    search_fields = ('manufacturer', 'battery_type_title')
    list_filter = ('manufacturer',)