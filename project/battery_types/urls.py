from django.urls import path
from . import views
from .views import BatteryTypeCreateView, BatteryTypeUpdateView, BatteryTypeDeleteView

urlpatterns = [
    path('battery_types', views.battery_types_view, name='battery_types'),
    path('add/', BatteryTypeCreateView.as_view(), name='battery_type_add'),
    path('<int:pk>/update/', BatteryTypeUpdateView.as_view(), name='battery_type_edit'),
    path('<int:pk>/detail/', views.battery_type_detail, name='battery_type_detail'),
    path('<int:pk>/delete/', BatteryTypeDeleteView.as_view(), name='battery_type_confirm_delete'),
]