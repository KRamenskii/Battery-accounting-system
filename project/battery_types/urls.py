from django.urls import path
from . import views

urlpatterns = [
    path('battery_types', views.battery_types_view, name='battery_types')
]