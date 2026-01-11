from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event

# Функция для парсинга даты
def parse_custom_date(date_str):
        """Парсит дату из строки с поддержкой разных форматов."""
        if not date_str:
            return None
        
        # Пробуем разные форматы
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y.%m.%d', '%Y/%m/%d'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

def events_list(request):
    events = Event.objects.all().order_by('-timestamp')
    
    # Получаем список пользователей для фильтра
    User = get_user_model()  # Используем get_user_model()
    users_with_events = User.objects.filter(
        event__isnull=False
    ).distinct().order_by('username')

    # Определяем доступные модели для фильтрации
    from django.contrib.contenttypes.models import ContentType
    
    # Модели, которые мы отслеживаем
    watched_models = {
        "journal.installationlocation": "Место установки",
        "journal.battery": "Аккумуляторная батарея",
        "journal.serialparameters": "Серийные параметры",
        "journal.batteryinstallationhistory": "История установки АБ",
        "journal.testingdbt12d": "Тестирование DBT12D",
        "journal.testingic105": "Тестирование IC105",
        "battery_types.batterytype": "Тип АБ",
    }
    
    # Получаем ContentType для отображения
    content_types = []
    for model_key, model_name in watched_models.items():
        try:
            app_label, model = model_key.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
            content_types.append({
                'id': ct.id,
                'name': model_name,
                'app_label': app_label,
                'model': model
            })
        except ContentType.DoesNotExist:
            continue
    
    # Получаем выбранный тип объекта из GET-параметров
    selected_content_type = request.GET.get('content_type', '')
    
    # Фильтруем события по типу объекта, если выбран
    if selected_content_type:
        try:
            ct = ContentType.objects.get(id=selected_content_type)
            events = events.filter(content_type=ct)
        except (ContentType.DoesNotExist, ValueError):
            pass
    
    # Типы событий для фильтра
    event_types = Event.EVENT_TYPE_CHOICES
    
    # Получаем фильтры из GET параметров
    selected_user = request.GET.get('user')
    selected_event_type = request.GET.get('event_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Применяем фильтр по пользователю
    if selected_user and selected_user != 'all':
        try:
            user_id = int(selected_user)
            events = events.filter(user_id=user_id)
        except (ValueError, TypeError):
            pass
    
    # Применяем фильтр по типу события
    if selected_event_type and selected_event_type != 'all':
        events = events.filter(event_type=selected_event_type)
    
    # Применяем фильтр по дате "С"
    if date_from:
        try:
            # Пробуем разные форматы дат
            date_obj = None
            for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    date_obj = datetime.strptime(date_from, fmt).date()
                    break
                except ValueError:
                    continue
            
            if date_obj:
                # Конвертируем в datetime для фильтрации
                date_from_dt = timezone.make_aware(
                    datetime.combine(date_obj, datetime.min.time())
                )
                events = events.filter(timestamp__gte=date_from_dt)
        except (ValueError, TypeError):
            pass
    
    # Применяем фильтр по дате "По"
    if date_to:
        try:
            date_obj = None
            for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    date_obj = datetime.strptime(date_to, fmt).date()
                    break
                except ValueError:
                    continue
            
            if date_obj:
                date_to_dt = timezone.make_aware(
                    datetime.combine(date_obj, datetime.max.time())
                )
                events = events.filter(timestamp__lte=date_to_dt)
        except (ValueError, TypeError):
            pass
    
    # Генерация ссылок для быстрых фильтров по дате
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Подготавливаем даты для отображения в шаблоне
    # Конвертируем строки дат в формат для отображения
    def format_date_for_display(date_str):
        date_obj = parse_custom_date(date_str)
        if date_obj:
            return date_obj.strftime('%d.%m.%Y')
        return date_str
    
    # Подсчет событий для статистики
    total_events = events.count()
    create_count = events.filter(event_type='create').count()
    update_count = events.filter(event_type='update').count()
    delete_count = events.filter(event_type='delete').count()

    paginator = Paginator(events, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "events/events_list.html", {
        "page_obj": page_obj,
        "users": users_with_events,
        "event_types": event_types,
        "selected_user": selected_user,
        "selected_event_type": selected_event_type,
        "date_from": date_from,
        "date_to": date_to,
        "date_from_display": format_date_for_display(date_from) if date_from else None,
        "date_to_display": format_date_for_display(date_to) if date_to else None,
        "total_events": total_events,
        "create_count": create_count,
        "update_count": update_count,
        "delete_count": delete_count,
        'content_types': content_types,
        'selected_content_type': selected_content_type,
        "today": today.strftime('%Y-%m-%d'),
        "yesterday": yesterday.strftime('%Y-%m-%d'),
        "week_ago": week_ago.strftime('%Y-%m-%d'),
        "month_ago": month_ago.strftime('%Y-%m-%d'),
    })