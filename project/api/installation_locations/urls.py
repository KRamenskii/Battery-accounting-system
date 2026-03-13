from django.urls import path
from .views import (
    InstallationLocationListCreateAPIView,
    InstallationLocationDetailAPIView
)

urlpatterns = [
    path('', InstallationLocationListCreateAPIView.as_view()),
    path('<int:pk>/', InstallationLocationDetailAPIView.as_view()),
]