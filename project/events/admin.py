# events/admin.py
from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "user", "content_type", "object_id", "timestamp")
    readonly_fields = ("user", "event_type", "timestamp", "content_type", "object_id", "object_repr", "old_data", "new_data", "changed_fields")