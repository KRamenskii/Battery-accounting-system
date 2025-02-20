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
]