from django.contrib import admin
from .models import InstallationLocation, Battery, TestingDBT12D, TestingIC105, BatteryInstallationHistory

@admin.register(InstallationLocation)
class InstallationLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'location_title', 'parent_location', 'nesting_level')
    search_fields = ('location_title',)
    list_filter = ('nesting_level',)

@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial_number', 'battery_number', 'battery_type', 'manufacture_date')
    search_fields = ('serial_number', 'battery_number')
    list_filter = ('battery_type',)

@admin.register(TestingDBT12D)
class TestingDBT12DAdmin(admin.ModelAdmin):
    list_display = ('id', 'battery', 'testing_date', 'SOH', 'SOC', 'VOL', 'R', 'STD', 'CCA')
    list_filter = ('testing_date',)

@admin.register(TestingIC105)
class TestingIC105Admin(admin.ModelAdmin):
    list_display = ('id', 'battery', 'testing_date', 'SOH', 'VOL', 'R', 'STD', 'CCA')
    list_filter = ('testing_date',)

@admin.register(BatteryInstallationHistory)
class BatteryInstallationHistory(admin.ModelAdmin):
    list_display = ('id', 'battery', 'installation_location', 'installation_date')
    list_filter = ('installation_date', 'installation_location')
    search_fields = ('battery__battery_number', 'installation_location__location_title')