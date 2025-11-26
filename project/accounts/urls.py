from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('personal-account/', views.personal_account, name='personal_account'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_error/', views.ErrorReportCreateView.as_view(), name='add_error_report'),
    path('error-reports/', views.error_reports, name='error_reports'),
    path('error-reports/delete/<int:error_id>/', views.delete_error_report, name='delete_error'),
]