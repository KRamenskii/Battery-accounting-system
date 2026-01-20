from django.urls import path
from .views import (
    SerialParametersListCreateAPIView,
    SerialParametersDetailAPIView
)

urlpatterns = [
    path('', SerialParametersListCreateAPIView.as_view()),
    path('<int:pk>/', SerialParametersDetailAPIView.as_view()),
]