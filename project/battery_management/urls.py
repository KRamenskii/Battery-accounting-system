from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('journal/', include('journal.urls')),
    path('battery_types/', include('battery_types.urls')),
    path('homepage/', include('homepage.urls')),
    path('events/', include('events.urls')),
]