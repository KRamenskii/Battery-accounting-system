from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Event(models.Model):

    EVENT_TYPE_CHOICES = [
        ("create", "Создание"),
        ("update", "Редактирование"),
        ("delete", "Удаление"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь"
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name="Тип события")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    old_data = models.JSONField(null=True, blank=True, verbose_name="Старые данные")
    new_data = models.JSONField(null=True, blank=True, verbose_name="Новые данные")
    changed_fields = models.JSONField(null=True, blank=True, verbose_name="Изменённые поля")

    object_repr = models.CharField(max_length=255, blank=True, null=True, verbose_name="Объект")

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_event_type_display()} — {self.content_type.app_label}.{self.content_type.model} #{self.object_id}"