from django.urls import path
from . import views
from .views import InstallationLocationCreateView, InstallationLocationUpdateView, InstallationLocationDeleteView

urlpatterns = [
    path('', views.journal_view, name='journal'),
    path('<int:location_id>/', views.journal_view, name='journal_filtered'),
    path('installation_locations/', views.installation_locations, name='installation_locations'),
    path('installation_locations/<int:location_id>/', views.installation_locations, name='installation_locations'),
    path('installation_locations/<int:pk>/delete/', InstallationLocationDeleteView.as_view(), name='installation_location_confirm_delete'),
    path('installation_locations/<int:pk>/update/', InstallationLocationUpdateView.as_view(), name='installation_location_edit'),
    path('add/', InstallationLocationCreateView.as_view(), name='installation_location_add'),
    path('<int:pk>/detail/', views.battery_detail, name='battery_detail'),
    path('add_testing_dbt12d/<int:battery_id>/', views.TestingDBT12DCreateView.as_view(), name='add_testing_dbt12d'),
    path('add_testing_ic105/<int:battery_id>/', views.TestingIC105CreateView.as_view(), name='add_testing_ic105'),
    path('battery_detail/<int:pk>/update/', views.BatteryUpdateView.as_view(), name='battery_detail_edit'),
    path('add_battery/', views.BatteryCreateView.as_view(), name='add_battery'),
    path('add_installation_location_battery/<int:battery_id>/', views.BatteryInstallationHistoryCreateView.as_view(), name='add_installation_location_battery'),
    path('test/delete/<str:test_type>/<int:test_id>/', views.delete_test, name='delete_test'),
    path('installation/delete/<int:installation_id>/', views.delete_installation, name='delete_installation'),
    path('battery/<int:battery_id>/parameters/', views.battery_detail_parameters, name='battery_detail_parameters'),
    
    # API для получения данных
    path('api/test/dbt12d/<int:test_id>/', views.get_test_dbt12d, name='api_get_test_dbt12d'),
    path('api/test/ic105/<int:test_id>/', views.get_test_ic105, name='api_get_test_ic105'),
    path('api/installation/<int:installation_id>/', views.get_installation_history, name='api_get_installation_history'),
    
    # API для обновления данных
    path('api/test/dbt12d/<int:test_id>/update/', views.update_test_dbt12d, name='api_update_test_dbt12d'),
    path('api/test/ic105/<int:test_id>/update/', views.update_test_ic105, name='api_update_test_ic105'),
    path('api/installation/<int:installation_id>/update/', views.update_installation_history, name='api_update_installation_history'),
]