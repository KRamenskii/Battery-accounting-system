from django.urls import path
from .views import (
    BatteryTypeListCreateAPIView,
    BatteryTypeDetailAPIView
)

urlpatterns = [
    path('', BatteryTypeListCreateAPIView.as_view()),
    path('<int:pk>/', BatteryTypeDetailAPIView.as_view()),
]