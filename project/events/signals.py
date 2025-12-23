import json
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db import models

import decimal
import datetime

from .models import Event
from .middleware import get_current_user

WATCHED_MODELS = {
    "journal.installationlocation",
    "journal.battery",
    "journal.serialparameters",
    "journal.batteryinstallationhistory",
    "journal.testingdbt12d",
    "journal.testingic105",
    "battery_types.batterytype",
}

def get_related_object_data(obj):
    """Получает читаемые данные связанного объекта"""
    if not obj:
        return None
    
    data = {'id': obj.id}
    
    # Добавляем читаемые поля в зависимости от типа объекта
    if hasattr(obj, 'serial_number'):
        data['serial_number'] = obj.serial_number
    elif hasattr(obj, 'battery_type_title'):
        data['battery_type_title'] = obj.battery_type_title
    elif hasattr(obj, 'location_title'):
        data['location_title'] = obj.location_title
    elif hasattr(obj, 'system_title'):
        data['system_title'] = obj.system_title
    elif hasattr(obj, 'battery_number'):
        data['battery_number'] = obj.battery_number
    elif hasattr(obj, 'username'):
        data['username'] = obj.username
    elif hasattr(obj, 'email'):
        data['email'] = obj.email
    elif hasattr(obj, 'name'):
        data['name'] = obj.name
    elif hasattr(obj, 'title'):
        data['title'] = obj.title
    elif hasattr(obj, '__str__'):
        data['display_name'] = str(obj)
    
    return data

def get_enriched_model_to_dict(instance):
    """Расширенная версия model_to_dict с данными связанных объектов"""
    from django.forms.models import model_to_dict
    
    # Получаем базовый словарь
    data = model_to_dict(instance)
    
    # Обрабатываем ForeignKey поля
    for field in instance._meta.get_fields():
        if (field.many_to_one or field.one_to_one) and field.concrete:
            field_name = field.name
            if field_name in data:
                related_obj = getattr(instance, field_name, None)
                if related_obj:
                    data[field_name] = get_related_object_data(related_obj)
    
    return data

# ---------------------- UTILS ----------------------

def get_full_representation(instance):
    """Безопасное получение полного представления с fallback"""
    if hasattr(instance, 'full_representation'):
        try:
            return instance.full_representation()
        except:
            pass
    # Fallback на обычный __str__
    return str(instance)

def normalize_for_json(value):
    """Преобразуем значение к JSON-safe представлению."""
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_for_json(v) for v in value]
    return value

def normalize_dict_for_json(d: dict):
    return {k: normalize_for_json(v) for k, v in d.items()}

def get_model_key(instance):
    return f"{instance._meta.app_label}.{instance._meta.model_name}"

# Храним "сырое" старое состояние (без приведения Decimal->float)
_PREVIOUS_RAW = {}

@receiver(pre_save)
def store_old_state(sender, instance, **kwargs):
    model_key = get_model_key(instance)
    if model_key not in WATCHED_MODELS:
        return

    # Для create нет старого состояния
    if not instance.pk:
        return

    old = sender.objects.filter(pk=instance.pk).first()
    if not old:
        return

    # Сохраняем ОБА представления
    _PREVIOUS_RAW[instance.pk] = {
        'data': get_enriched_model_to_dict(old),
        'repr': str(old),  # короткое (__str__)
        'full_repr': get_full_representation(old)  # полное
    }

# ---------------------- СРАВНЕНИЕ ПО ТИПУ ----------------------

def field_values_equal(model_class, field_name, old_val, new_val):
    """
    Сравнивает старое и новое значение с учетом типа поля модели.
    """
    try:
        field = model_class._meta.get_field(field_name)
    except Exception:
        return old_val == new_val

    # DecimalField
    if isinstance(field, models.DecimalField):
        try:
            if old_val is None and new_val is None:
                return True
            if old_val is None or new_val is None:
                return False
            return decimal.Decimal(old_val) == decimal.Decimal(new_val)
        except Exception:
            return str(old_val) == str(new_val)

    # Date / DateTime / Time
    if isinstance(field, (models.DateField, models.DateTimeField, models.TimeField)):
        if old_val is None and new_val is None:
            return True
        return str(old_val) == str(new_val)

    # ForeignKey - теперь это может быть словарь или число
    if isinstance(field, models.ForeignKey):
        try:
            # Если оба значения - словари, сравниваем по id
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                return old_val.get('id') == new_val.get('id')
            # Если одно из значений - число (старый формат)
            elif isinstance(old_val, (int, float)) or isinstance(new_val, (int, float)):
                old_id = old_val.get('id') if isinstance(old_val, dict) else old_val
                new_id = new_val.get('id') if isinstance(new_val, dict) else new_val
                return old_id == new_id
            else:
                return old_val == new_val
        except Exception:
            return str(old_val) == str(new_val)

    # По умолчанию
    return old_val == new_val

# ---------------------- MAIN SIGNALS ----------------------

@receiver(post_save)
def track_create_update(sender, instance, created, **kwargs):
    model_key = get_model_key(instance)
    if model_key not in WATCHED_MODELS:
        return

    # Сырой словарь текущего состояния (до нормализации)
    new_raw = get_enriched_model_to_dict(instance)
    old_raw = None
    changed_fields = None

    if created:
        event_type = "create"
        object_repr_value = str(instance)  # короткое
        full_repr_value = get_full_representation(instance)  # полное
    else:
        event_type = "update"
        old_data_dict = _PREVIOUS_RAW.get(instance.pk, {})
        old_raw = old_data_dict.get('data')
        
        # Для обновления используем СТАРОЕ полное представление
        object_repr_value = old_data_dict.get('repr', str(instance))  # короткое
        full_repr_value = old_data_dict.get('full_repr', get_full_representation(instance))  # полное

        if old_raw is None:
            # на всякий случай — попытка получить из БД (если pre_save не сработал)
            try:
                old_obj = sender.objects.get(pk=instance.pk)
                old_raw = get_enriched_model_to_dict(old_obj)
            except Exception:
                old_raw = None

        # сравниваем поле за полем, с учётом типов
        if old_raw:
            changed = []
            # учитываем все ключи из new_raw (и те, что были в old_raw)
            all_keys = set(new_raw.keys()) | set(old_raw.keys())
            for key in all_keys:
                old_val = old_raw.get(key)
                new_val = new_raw.get(key)
                if not field_values_equal(sender, key, old_val, new_val):
                    changed.append(key)
            if changed:
                changed_fields = changed

    # Готовим JSON-безопасные данные для хранения
    old_json = normalize_dict_for_json(old_raw) if old_raw is not None else None
    new_json = normalize_dict_for_json(new_raw) if new_raw is not None else None

    Event.objects.create(
        user=get_current_user(),
        event_type=event_type,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=object_repr_value,  # короткое представление
        full_representation=full_repr_value,  # ← НОВОЕ ПОЛЕ: полное представление
        old_data=old_json,
        new_data=new_json,
        changed_fields=changed_fields,
    )

    # очистка кеша
    if instance.pk in _PREVIOUS_RAW:
        del _PREVIOUS_RAW[instance.pk]

@receiver(post_delete)
def track_delete(sender, instance, **kwargs):
    model_key = get_model_key(instance)
    if model_key not in WATCHED_MODELS:
        return

    old_raw = get_enriched_model_to_dict(instance)
    old_json = normalize_dict_for_json(old_raw)

    # Получаем полное представление ПЕРЕД удалением
    full_repr_value = get_full_representation(instance)

    Event.objects.create(
        user=get_current_user(),
        event_type="delete",
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance),  # короткое
        full_representation=full_repr_value,  # ← полное представление
        old_data=old_json,
        new_data=None,
        changed_fields=None,
    )