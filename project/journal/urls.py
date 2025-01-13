from django.urls import path
from . import views

urlpatterns = [
    path('journal_home', views.journal_home, name='journal_home')
]
