from django.urls import path
from . import views

urlpatterns = [
    path('', views.journal_view, name='journal'),  # Все АКБ
    path('<int:location_id>/', views.journal_view, name='journal_filtered'),  # Фильтрация по местоположению
]