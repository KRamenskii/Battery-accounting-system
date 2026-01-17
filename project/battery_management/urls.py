from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('journal/', include('journal.urls')),
    path('battery_types/', include('battery_types.urls')),
    path('homepage/', include('homepage.urls')),
    path('events/', include('events.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)