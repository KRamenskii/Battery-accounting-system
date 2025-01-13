from django.urls import path
from . import views

urlpatterns = [
    path('battery_types', views.battery_types, name='battery_types')
]