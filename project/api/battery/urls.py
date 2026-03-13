from django.urls import path
from .views import (
    BatteryListCreateAPIView,
    BatteryDetailAPIView
)

urlpatterns = [
    path('', BatteryListCreateAPIView.as_view()),
    path('<int:pk>/', BatteryDetailAPIView.as_view()),
]