from django.urls import path
from . import views
from .views import BatteryTypeCreateView

urlpatterns = [
    path('battery_types', views.battery_types_view, name='battery_types'),
    path('add/', BatteryTypeCreateView.as_view(), name='battery_type_add')
]