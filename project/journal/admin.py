from django.contrib import admin
from .models import InstallationLocation, Battery, TestingDBT12D, TestingIC105, BatteryInstallationHistory, SerialParameters
from .forms import BatteryAdminForm

@admin.register(InstallationLocation)
class InstallationLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'location_title', 'parent_location', 'nesting_level')
    search_fields = ('location_title',)
    list_filter = ('nesting_level',)

@admin.register(SerialParameters)
class SerialParametersAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'battery_type', 'manufacture_date')
    list_filter = ('battery_type',)
    search_fields = ('serial_number',)

# @admin.register(Battery)
# class BatteryAdmin(admin.ModelAdmin):
#     list_display = ('battery_number', 'battery_type', 'get_serial_number', 'get_manufacture_date', 'acceptance_date')
#     list_filter = ('battery_type',)
#     search_fields = ('battery_number',)
    
#     # Добавляем методы для отображения связанных данных
#     def get_serial_number(self, obj):
#         return obj.serial_parameters.serial_number if obj.serial_parameters else "Не указан"
#     get_serial_number.short_description = 'Серийный номер'
#     get_serial_number.admin_order_field = 'serial_parameters__serial_number'  # Для сортировки
    
#     def get_manufacture_date(self, obj):
#         return obj.serial_parameters.manufacture_date if obj.serial_parameters else "Не указана"
#     get_manufacture_date.short_description = 'Дата изготовления'
#     get_manufacture_date.admin_order_field = 'serial_parameters__manufacture_date'  # Для сортировки

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

@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    form = BatteryAdminForm  # Используем нашу кастомную форму
    list_display = ('battery_number', 'battery_type', 'get_serial_number', 'get_manufacture_date', 'acceptance_date')
    list_filter = ('battery_type',)
    search_fields = ('battery_number',)
    
    def get_serial_number(self, obj):
        return obj.serial_parameters.serial_number if obj.serial_parameters else "Не указан"
    get_serial_number.short_description = 'Серийный номер'
    get_serial_number.admin_order_field = 'serial_parameters__serial_number'
    
    def get_manufacture_date(self, obj):
        return obj.serial_parameters.manufacture_date if obj.serial_parameters else "Не указана"
    get_manufacture_date.short_description = 'Дата изготовления'
    get_manufacture_date.admin_order_field = 'serial_parameters__manufacture_date'