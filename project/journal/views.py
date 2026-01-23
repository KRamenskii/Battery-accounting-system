from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import io
from PIL import Image, ImageDraw, ImageFont
import os

from .models import Battery, BatteryInstallationHistory, InstallationLocation, TestingDBT12D, TestingIC105
from .forms import InstallationLocationForm, TestingDBT12DForm, TestingIC105Form, BatteryForm, BatteryInstallationHistoryForm, BatteryUpdateForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = os.path.join(BASE_DIR, 'fonts', 'Roboto-Regular.ttf')
FONT_BOLD = os.path.join(BASE_DIR, 'fonts', 'Roboto-Bold.ttf')


class InstallationLocationCreateView(CreateView):
    model = InstallationLocation
    form_class = InstallationLocationForm
    template_name = 'journal/installation_location_create.html'

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('installation_locations')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER', '')
        current_url = self.request.build_absolute_uri()
        if referer != current_url:
            context['next_param'] = referer
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        parent_id = self.request.GET.get('parent_id')
        if parent_id:
            kwargs['parent_location'] = get_object_or_404(InstallationLocation, id=parent_id)
        return kwargs


class InstallationLocationUpdateView(UpdateView):
    model = InstallationLocation
    form_class = InstallationLocationForm
    template_name = 'journal/installation_location_edit.html'
    context_object_name = 'installation_location_edit'

    def get_success_url(self):
        # Получаем next из GET или POST
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('installation_locations')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем текущий referer как параметр next
        referer = self.request.META.get('HTTP_REFERER', '')
        # Проверяем, что это не текущая страница редактирования
        current_url = self.request.build_absolute_uri()
        if referer != current_url:
            context['next_param'] = referer
        return context


class InstallationLocationDeleteView(DeleteView):
    model = InstallationLocation
    template_name = 'journal/installation_location_confirm_delete.html'
    context_object_name = 'installation_location_confirm_delete'

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('installation_locations')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER', '')
        current_url = self.request.build_absolute_uri()
        if referer != current_url:
            context['next_param'] = referer
        return context


class TestingDBT12DCreateView(CreateView):
    model = TestingDBT12D
    form_class = TestingDBT12DForm
    template_name = 'journal/add_testing.html'

    def get_initial(self):
        initial = super().get_initial()
        battery_id = self.kwargs.get('battery_id')  # Получаем ID АБ из URL
        battery = get_object_or_404(Battery, id=battery_id)
        initial['battery'] = battery  # Предзаполняем поле battery
        return initial
    
    def get_success_url(self):
        # Проверяем параметр next из POST (из скрытого поля)
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        
        # Если нет next, возвращаем с сохранением GET-параметров
        params = self.request.GET.urlencode()
        url = reverse('battery_detail', kwargs={'pk': self.object.battery.id})
        return f"{url}?{params}" if params else url


class TestingIC105CreateView(CreateView):
    model = TestingIC105
    form_class = TestingIC105Form
    template_name = 'journal/add_testing.html'

    def get_initial(self):
        initial = super().get_initial()
        battery_id = self.kwargs.get('battery_id')  # Получаем ID АБ из URL
        battery = get_object_or_404(Battery, id=battery_id)
        initial['battery'] = battery  # Предзаполняем поле battery
        return initial
    
    def get_success_url(self):
        # Проверяем параметр next из POST (из скрытого поля)
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        
        # Если нет next, возвращаем с сохранением GET-параметров
        params = self.request.GET.urlencode()
        url = reverse('battery_detail', kwargs={'pk': self.object.battery.id})
        return f"{url}?{params}" if params else url


class BatteryUpdateView(UpdateView):
    model = Battery
    form_class = BatteryUpdateForm
    template_name = 'journal/battery_detail_edit.html'
    context_object_name = 'battery_detail_edit'

    def get_initial(self):
        initial = super().get_initial()
        battery = self.get_object()
        installation_locations = BatteryInstallationHistory.objects.filter(battery=battery).order_by('-installation_date')
        
        if installation_locations.exists():
            initial['installation_location'] = installation_locations.first().installation_location

        return initial

    def get_success_url(self):
        return reverse_lazy('battery_detail', kwargs={'pk': self.object.id})


class BatteryCreateView(CreateView):
    model = Battery
    form_class = BatteryForm
    template_name = 'journal/add_battery.html'
    success_url = reverse_lazy('journal')

    def get_initial(self):
        initial = super().get_initial()
        selected_location_id = self.request.GET.get('selected_location_id')
        if selected_location_id:
            initial['installation_location'] = get_object_or_404(InstallationLocation, id=selected_location_id)

        battery_type_id = self.request.GET.get('battery_type')
        if battery_type_id:
            initial['battery_type'] = battery_type_id  # достаточно id
        return initial

    def get_success_url(self):
        selected_location_id = self.request.POST.get('installation_location')
        return reverse('journal_filtered', kwargs={'location_id': selected_location_id})


class BatteryInstallationHistoryCreateView(CreateView):
    model = BatteryInstallationHistory
    form_class = BatteryInstallationHistoryForm
    template_name = 'journal/add_installation_location_battery.html'

    def get_initial(self):
        initial = super().get_initial()
        battery_id = self.kwargs.get('battery_id')
        battery = get_object_or_404(Battery, id=battery_id)
        
        # Берем action из GET-параметра (если есть)
        action = self.request.GET.get('action')
        
        # Всегда предзаполняем аккумулятор
        initial['battery'] = battery
        
        # Текущая дата по умолчанию
        initial['installation_date'] = timezone.now().date()
        
        # Предзаполняем location только если указан action
        if action:
            location_map = {
                'utilization': 'Утилизация',
                'warehouse': 'Склад',
                'archive': 'Архив',
            }
            
            if action in location_map:
                location, _ = InstallationLocation.objects.get_or_create(
                    location_title=location_map[action],
                    defaults={'description': f'Место: {location_map[action]}'}
                )
                initial['installation_location'] = location
                
                # Можно добавить заметку
                if action == 'utilization':
                    initial['notes'] = 'Перемещено в утилизацию'
        
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        battery_id = self.kwargs.get('battery_id')
        kwargs['battery'] = get_object_or_404(Battery, id=battery_id)  # Передаем аккумулятор в форму
        return kwargs

    def get_success_url(self):
        # Проверяем параметр next из POST (из скрытого поля)
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        
        # Если нет next, возвращаем с сохранением GET-параметров
        params = self.request.GET.urlencode()
        url = reverse('battery_detail', kwargs={'pk': self.object.battery.id})
        return f"{url}?{params}" if params else url


def get_last_installation():
    """Получаем только последнее место установки АБ"""
    return BatteryInstallationHistory.objects.filter(
        battery=OuterRef("pk")
    ).order_by("-installation_date").values("installation_location_id")[:1]


def get_child_locations(parent_id):
    """Рекурсивно получаем все дочерние местоположения"""
    children = InstallationLocation.objects.filter(parent_location_id=parent_id)
    child_ids = list(children.values_list('id', flat=True))
    for child_id in child_ids:
        child_ids.extend(get_child_locations(child_id))
    return child_ids


def get_all_parents(location):
    """Рекурсивно получаем всех родителей местоположения"""
    parents = []
    while location.parent_location:
        parents.append(location.parent_location.id)
        location = location.parent_location
    return parents


def get_parent_locations(location):
    """Рекурсивно получаем всех родителей местоположения в правильном порядке"""
    parents = []
    while location.parent_location:
        parents.insert(0, location.parent_location)  # Вставляем в начало списка
        location = location.parent_location
    return parents


def journal_view(request, location_id=None):
    q = request.GET.get("q")

    is_search = False
    search_not_found = False
    found_battery = None
    similar_locations = []

    if q:
        q = q.strip()
        is_search = True

        # ===== Поиск по номеру АБ (ТОЧНОЕ совпадение) =====
        if q.isdigit():
            found_battery = Battery.objects.filter(
                battery_number=q
            ).first()

            if found_battery:
                last_installation = (
                    BatteryInstallationHistory.objects
                    .filter(battery=found_battery)
                    .order_by("-installation_date")
                    .first()
                )

                if last_installation:
                    location_id = last_installation.installation_location_id
                    # Получаем количество АБ в этом месте
                    battery_count_in_location = BatteryInstallationHistory.objects.filter(
                        installation_location_id=location_id,
                        id__in=Subquery(
                            BatteryInstallationHistory.objects.filter(
                                battery=OuterRef('battery')
                            ).order_by('-installation_date').values('id')[:1]
                        )
                    ).count()
                    
                    # Если больше 8 АБ, запоминаем ID найденной батареи для фильтрации
                    if battery_count_in_location > 8:
                        request.session['search_only_battery_id'] = found_battery.id
            else:
                search_not_found = True

        # ===== Поиск по месту установки =====
        else:
            q_clean = q.strip().lower()
            
            # Загружаем все места в память
            all_locations = list(InstallationLocation.objects.all())
            
            location = None
            similar = []
            
            for loc in all_locations:
                loc_title_lower = loc.location_title.lower()
                
                # Точное совпадение
                if loc_title_lower == q_clean:
                    location = loc
                    break
                
                # Похожие места
                if q_clean in loc_title_lower:
                    similar.append(loc)
            
            if location:
                location_id = location.id
                request.session.pop('search_only_battery_id', None)
            else:
                similar_locations = similar
                search_not_found = True

    # Очищаем флаг, если это не поиск
    if not is_search:
        request.session.pop('search_query', None)
        request.session.pop('search_only_battery_id', None)

    """Отображение страницы журнала с учетом фильтрации по местоположению и типу АБ"""
    # Получаем параметр фильтрации по типу из GET-запроса
    battery_type_id = request.GET.get('type')
    soh_filter = request.GET.get('soh', 'all')
    date_filter = request.GET.get('date_filter', 'all')
    search_query = request.GET.get('q', '')

    last_installation_subquery = BatteryInstallationHistory.objects.filter(
        battery=OuterRef("pk")
    ).order_by("-installation_date").values("installation_location_id")[:1]

    batteries = Battery.objects.annotate(
        last_location=Subquery(last_installation_subquery)
    )

    # +++ НОВЫЙ КОД: если есть флаг поиска по одной батарее, фильтруем только её +++
    if is_search and 'search_only_battery_id' in request.session:
        batteries = batteries.filter(id=request.session['search_only_battery_id'])

    # Применяем фильтр по типу АБ, если он задан
    if battery_type_id and battery_type_id != 'all':
        batteries = batteries.filter(battery_type_id=battery_type_id)
    
    # Применяем фильтр по состоянию (SOH)
    if soh_filter != 'all':
        latest_soh_subquery = TestingDBT12D.objects.filter(
            battery=OuterRef('pk')
        ).order_by('-testing_date').values('SOH')[:1]
        
        batteries = batteries.annotate(last_soh_value=Subquery(latest_soh_subquery))
        
        if soh_filter == 'good':
            batteries = batteries.filter(last_soh_value__gte=80)
        elif soh_filter == 'normal':
            batteries = batteries.filter(last_soh_value__gte=60, last_soh_value__lt=80)
        elif soh_filter == 'poor':
            batteries = batteries.filter(last_soh_value__gte=40, last_soh_value__lt=60)
        elif soh_filter == 'critical':
            batteries = batteries.filter(last_soh_value__lt=40)
        elif soh_filter == 'no_data':
            batteries = batteries.filter(last_soh_value__isnull=True)
    else:
        latest_soh_subquery = TestingDBT12D.objects.filter(
            battery=OuterRef('pk')
        ).order_by('-testing_date').values('SOH')[:1]
        batteries = batteries.annotate(last_soh_value=Subquery(latest_soh_subquery))
    
    # Применяем фильтр по дате последнего измерения
    if date_filter != 'all':
        from datetime import datetime, timedelta
        today = datetime.now().date()

        latest_date_subquery = TestingDBT12D.objects.filter(
            battery=OuterRef('pk')
        ).order_by('-testing_date').values('testing_date')[:1]
        
        batteries = batteries.annotate(last_test_date=Subquery(latest_date_subquery))
        
        if date_filter == 'no_data':
            batteries = batteries.filter(last_test_date__isnull=True)
        elif date_filter == 'lt3':
            threshold_date = today - timedelta(days=90)
            batteries = batteries.filter(last_test_date__gte=threshold_date)
        elif date_filter == 'gt3':
            threshold_date = today - timedelta(days=90)
            batteries = batteries.filter(last_test_date__lt=threshold_date)
        elif date_filter == 'lt6':
            threshold_date = today - timedelta(days=180)
            batteries = batteries.filter(last_test_date__gte=threshold_date)
        elif date_filter == 'gt6':
            threshold_date = today - timedelta(days=180)
            batteries = batteries.filter(last_test_date__lt=threshold_date)
        elif date_filter == 'gt9':
            threshold_date = today - timedelta(days=270)
            batteries = batteries.filter(last_test_date__lt=threshold_date)
        elif date_filter == 'gt12':
            threshold_date = today - timedelta(days=365)
            batteries = batteries.filter(last_test_date__lt=threshold_date)
    else:
        latest_date_subquery = TestingDBT12D.objects.filter(
            battery=OuterRef('pk')
        ).order_by('-testing_date').values('testing_date')[:1]
        batteries = batteries.annotate(last_test_date=Subquery(latest_date_subquery))

    used_locations = set(batteries.values_list("last_location", flat=True))
    parent_ids = set()

    for loc_id in used_locations:
        if loc_id:
            location = InstallationLocation.objects.get(id=loc_id)
            parent_ids.update(get_all_parents(location))

    valid_locations = used_locations | parent_ids
    locations = InstallationLocation.objects.filter(id__in=valid_locations, nesting_level=0)

    if location_id:
        selected_location = get_object_or_404(InstallationLocation, id=location_id)
        parent_locations = get_parent_locations(selected_location)
        child_location_ids = get_child_locations(location_id)
        locations = InstallationLocation.objects.filter(
            parent_location=location_id, id__in=valid_locations
        )
        batteries = batteries.filter(last_location__in=[location_id] + child_location_ids)
    else:
        selected_location = None
        parent_locations = []
        batteries = batteries.filter(last_location__isnull=False)

    latest_test_subquery = TestingDBT12D.objects.filter(
        battery=OuterRef('pk')
    ).order_by('-testing_date').values('testing_date')[:1]

    latest_vol_subquery = TestingDBT12D.objects.filter(
        battery=OuterRef('pk')
    ).order_by('-testing_date').values('VOL')[:1]

    batteries = batteries.annotate(
        last_testing_date=Subquery(latest_test_subquery),
        last_vol=Subquery(latest_vol_subquery)
    )

    # Получаем только те типы АБ, которые есть в отфильтрованном наборе
    battery_types = batteries.order_by('battery_type__battery_type_title') \
                           .values_list('battery_type__id', 'battery_type__battery_type_title') \
                           .distinct()

    journal_data = []
    for index, battery in enumerate(batteries, start=1):
        soh_value = battery.last_soh_value
        
        if soh_value is None:
            soh_display = "Нет данных"
            soh_numeric = 0
        else:
            soh_display = f"{soh_value:.0f}%"
            soh_numeric = float(soh_value)
        
        journal_data.append({
            "index": index,
            "installation_location": InstallationLocation.objects.get(
                id=battery.last_location
            ).location_title if battery.last_location else "Не установлено",
            "battery_number": battery.battery_number,
            "battery_type": battery.battery_type.battery_type_title,
            "testing_date": battery.last_testing_date or "Нет данных",
            "soh": soh_numeric,
            "soh_display": soh_display,
            "vol": battery.last_vol,
            "battery_id": battery.id,
            "last_test_date": battery.last_test_date,
        })

    paginator = Paginator(journal_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'journal/journal.html', {
        "page_obj": page_obj,
        "locations": locations,
        "selected_location": selected_location,
        "parent_locations": parent_locations,
        "selected_location_id": selected_location.id if selected_location else None,
        "battery_types": battery_types,
        "selected_battery_type": int(battery_type_id) if battery_type_id and battery_type_id != 'all' else None,
        "selected_soh_filter": soh_filter,
        "selected_date_filter": date_filter,
        "is_search": is_search,
        "search_query": q,
        "search_not_found": search_not_found,
        'is_numeric': search_query.lstrip('-').replace('.', '', 1).isdigit(),
        "similar_locations": similar_locations,
    })


def installation_locations(request, location_id=None):
    selected_location = None
    parent_locations = []

    if location_id:
        selected_location = get_object_or_404(InstallationLocation, id=location_id)
        locations = InstallationLocation.objects.filter(parent_location=selected_location)

        if selected_location.parent_location is not None:
            parent_locations = get_parent_locations(selected_location)

    else:
        locations = InstallationLocation.objects.filter(nesting_level=0)

    return render(request, 'journal/installation_locations.html', {
        'locations': locations,
        'selected_location': selected_location,
        'parent_locations': parent_locations,
    })


def battery_detail(request, pk):
    battery = get_object_or_404(Battery, pk=pk)
    testings_dbt12d = TestingDBT12D.objects.filter(battery=battery).order_by('testing_date')
    testings_ic105 = TestingIC105.objects.filter(battery=battery).order_by('testing_date')
    installation_locations = BatteryInstallationHistory.objects.filter(battery=battery).order_by('installation_date')
    location_id = installation_locations.last().installation_location.id

    # Получаем все места установки для выпадающего списка
    all_installation_locations = InstallationLocation.objects.all()

    # Определяем заголовки, которые нужно скрыть
    hide_system_for_locations = ['Архив', 'Склад', 'Утилизация']

    # ВАЖНО: Получаем предыдущий location_id из GET-параметра
    previous_location_id = request.GET.get('from_location') or request.session.get('saved_location_id')
    previous_page = request.GET.get('page') or request.session.get('saved_page', 1)

    # Сохраняем в сессии
    if previous_location_id:
        request.session['saved_location_id'] = previous_location_id
    if previous_page:
        request.session['saved_page'] = previous_page

    # Если не передан, пытаемся взять из сессии
    if not previous_location_id:
        previous_location_id = request.session.get('previous_location_id')
    else:
        # Сохраняем в сессии на будущее
        request.session['previous_location_id'] = previous_location_id

    # Формируем пути для каждой записи
    installations_path = []
    for location in installation_locations:
        path = get_parent_locations(location.installation_location) + [location.installation_location]
        installations_path.append({
            'history': location,  # Сама запись истории
            'path': path,         # Путь к местоположению
            'location_obj': location.installation_location  # Объект местоположения
        })

    return render(request, 'journal/battery_detail.html', {
        'battery': battery,
        'testings_dbt12d': testings_dbt12d,
        'testings_ic105': testings_ic105,
        'model_dbt12d': 'DBT12D',
        'model_ic105': 'IC105',
        'installation_locations': installation_locations,
        'installations_path': installations_path,
        'location_id': location_id,
        'previous_location_id': previous_location_id,  # Откуда пришли
        'previous_page': previous_page,
        'all_installation_locations': all_installation_locations,
        'hide_system_for_locations': hide_system_for_locations,
    })


def battery_detail_parameters(request, battery_id):
    battery = get_object_or_404(Battery, id=battery_id)
    
    # Получаем все GET-параметры для передачи обратно
    get_params = request.GET
    
    return render(request, 'journal/battery_detail_parameters.html', {
        'battery': battery,
        'get_params': get_params,  # Передаем все GET-параметры
    })


@require_POST
@csrf_exempt
def delete_test(request, test_type, test_id):
    try:
        if test_type == 'dbt12d':
            model = TestingDBT12D
        elif test_type == 'ic105':
            model = TestingIC105
        else:
            return JsonResponse({'error': 'Неизвестный тип теста'}, status=400)
        
        test = model.objects.get(id=test_id)
        test.delete()
        return JsonResponse({'success': True})
    except model.DoesNotExist:
        model_name = "DBT12D" if test_type == 'dbt12d' else "IC105"
        return JsonResponse({'error': f'Тест {model_name} не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def delete_installation(request, installation_id):
    try:
        installation_history = BatteryInstallationHistory.objects.get(id=installation_id)
        installation_history.delete()
        return JsonResponse({'success': True})
    except BatteryInstallationHistory.DoesNotExist:
        return JsonResponse({'error': 'Запись истории установки не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Редактирование результатов тестирования АБ и истории мест установок
# Для сериализации тестирований DBT12D
def serialize_test_dbt12d(test):
    return {
        "id": test.id,
        "battery_id": test.battery.id,
        "testing_date": test.testing_date.strftime("%Y-%m-%d"),
        "SOH": str(test.SOH),
        "SOC": str(test.SOC),
        "VOL": str(test.VOL),
        "R": str(test.R),
        "STD": str(test.STD),
        "CCA": str(test.CCA),
    }

# Для сериализации тестирований IC105
def serialize_test_ic105(test):
    return {
        "id": test.id,
        "battery_id": test.battery.id,
        "testing_date": test.testing_date.strftime("%Y-%m-%d"),
        "SOH": str(test.SOH),
        "VOL": str(test.VOL),
        "R": str(test.R),
        "STD": str(test.STD),
        "CCA": str(test.CCA),
    }

# Для сериализации истории установок
def serialize_installation_history(installation):
    return {
        "id": installation.id,
        "installation_location_id": installation.installation_location.id,
        "installation_date": installation.installation_date.strftime("%Y-%m-%d") if installation.installation_date else None,
        "battery_id": installation.battery.id,
    }

# API для получения данных тестирования DBT12D
@login_required
def get_test_dbt12d(request, test_id):
    test = get_object_or_404(TestingDBT12D, id=test_id)
    
    data = serialize_test_dbt12d(test)
    return JsonResponse(data)

# API для получения данных тестирования IC105
@login_required
def get_test_ic105(request, test_id):
    test = get_object_or_404(TestingIC105, id=test_id)
    
    data = serialize_test_ic105(test)
    return JsonResponse(data)

# API для получения данных истории установки
@login_required
def get_installation_history(request, installation_id):
    installation = get_object_or_404(BatteryInstallationHistory, id=installation_id)
    
    data = serialize_installation_history(installation)
    return JsonResponse(data)

# Обновление тестирования DBT12D
@login_required
@require_http_methods(["POST"])
def update_test_dbt12d(request, test_id):
    test = get_object_or_404(TestingDBT12D, id=test_id)
    
    errors = {}
    
    # Получаем данные
    testing_date = request.POST.get('testing_date')
    soh = request.POST.get('SOH')
    soc = request.POST.get('SOC')
    vol = request.POST.get('VOL')
    r = request.POST.get('R')
    std = request.POST.get('STD')
    cca = request.POST.get('CCA')
    
    # Валидация
    if not testing_date:
        errors['testing_date'] = ['Дата тестирования обязательна']
    
    numeric_fields = ['SOH', 'SOC', 'VOL', 'R', 'STD', 'CCA']
    for field in numeric_fields:
        value = request.POST.get(field)
        if value:
            try:
                float(value)
            except ValueError:
                errors[field] = ['Должно быть числом']
    
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
    # Обновляем данные
    try:
        if testing_date:
            test.testing_date = testing_date
        if soh is not None:
            test.SOH = soh
        if soc is not None:
            test.SOC = soc
        if vol is not None:
            test.VOL = vol
        if r is not None:
            test.R = r
        if std is not None:
            test.STD = std
        if cca is not None:
            test.CCA = cca
        
        test.save()
        return JsonResponse({'success': True, 'message': 'Тестирование обновлено'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Обновление тестирования IC105
@login_required
@require_http_methods(["POST"])
def update_test_ic105(request, test_id):
    test = get_object_or_404(TestingIC105, id=test_id)
    
    errors = {}
    
    testing_date = request.POST.get('testing_date')
    soh = request.POST.get('SOH')
    vol = request.POST.get('VOL')
    r = request.POST.get('R')
    std = request.POST.get('STD')
    cca = request.POST.get('CCA')
    
    if not testing_date:
        errors['testing_date'] = ['Дата тестирования обязательна']
    
    numeric_fields = ['SOH', 'VOL', 'R', 'STD', 'CCA']
    for field in numeric_fields:
        value = request.POST.get(field)
        if value:
            try:
                float(value)
            except ValueError:
                errors[field] = ['Должно быть числом']
    
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
    try:
        if testing_date:
            test.testing_date = testing_date
        if soh is not None:
            test.SOH = soh
        if vol is not None:
            test.VOL = vol
        if r is not None:
            test.R = r
        if std is not None:
            test.STD = std
        if cca is not None:
            test.CCA = cca
        
        test.save()
        return JsonResponse({'success': True, 'message': 'Тестирование обновлено'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# Обновление истории установки
@login_required
@require_http_methods(["POST"])
def update_installation_history(request, installation_id):
    installation = get_object_or_404(BatteryInstallationHistory, id=installation_id)
    
    errors = {}
    
    installation_location_id = request.POST.get('installation_location')
    installation_date = request.POST.get('installation_date')
    
    if not installation_location_id:
        errors['installation_location'] = ['Место установки обязательно']
    
    if not installation_date:
        errors['installation_date'] = ['Дата установки обязательна']
    
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    
    try:
        # Получаем объект места установки
        location = InstallationLocation.objects.get(id=installation_location_id)
        installation.installation_location = location
        installation.installation_date = installation_date
        installation.save()
        
        return JsonResponse({'success': True, 'message': 'История установки обновлена'})
    except InstallationLocation.DoesNotExist:
        errors['installation_location'] = ['Место установки не найдено']
        return JsonResponse({'success': False, 'errors': errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def download_battery_label(request, battery_id):
    """Генерирует и возвращает изображение этикетки АБ для скачивания."""
    battery = get_object_or_404(Battery, id=battery_id)
    installation_locations = BatteryInstallationHistory.objects.filter(battery=battery).order_by('installation_date')
    testings_dbt12d = TestingDBT12D.objects.filter(battery=battery).order_by('testing_date')

    # 1. ПАРАМЕТРЫ ИЗОБРАЖЕНИЯ
    # Размеры для этикетки 40x60 мм при 203 DPI
    width_px = 480
    height_px = 320
    # Создаем белое изображение
    img = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(img)

    # 2. ЗАГРУЗКА ШРИФТА (важно указать путь к существующему файлу)
    try:
        # Загружаем шрифт по локальному пути
        font_regular = ImageFont.truetype(FONT_REGULAR, 16)
        font_bold = ImageFont.truetype(FONT_BOLD, 16)
    except IOError:
        # Запасной вариант: используем системный шрифт
        try:
            # Попробуем найти стандартный системный шрифт
            font_big = ImageFont.truetype("arial.ttf", 16)  # Pillow сам ищет в системных папках[citation:1]
        except IOError:
            # Если и это не сработало, используем базовый (не поддерживает русский)
            font_big = ImageFont.load_default()
            print("Внимание: используется шрифт по умолчанию, кириллица не отобразится.")

    # 3. РИСУЕМ РАЗДЕЛИТЕЛЬНУЮ ЛИНИЮ
    # Вычисляем середину по ширине
    middle_x = width_px // 2
    
    # Рисуем линию от (x1, y1) до (x2, y2)
    # y1 = 20 (отступ сверху), y2 = height-20 (отступ снизу)
    draw.line(
        [(middle_x, 10), (middle_x, height_px - 10)],  # Координаты начала и конца
        fill='black',
        width=3
    )
    
    # 4. ПОДПИСЬ МЕСТА УСТАНОВКИ
    title_installation = f"Место установки:"
    bbox = draw.textbbox((0, 0), title_installation, font=font_regular)
    text_width_installation = bbox[2] - bbox[0]
    x_title_installation = ((width_px) // 2 - text_width_installation) // 2
    y_title_installation = 35
    draw.text((x_title_installation, y_title_installation), title_installation, fill='black', font=font_regular)

    # Теперь само место установки
    title_place = f"{installation_locations.last().installation_location.location_title}"
    bbox = draw.textbbox((0, 0), title_place, font=font_regular)
    text_width_installation = bbox[2] - bbox[0]
    x_title_installation = ((width_px) // 2 - text_width_installation) // 2
    y_title_installation = 55
    draw.text((x_title_installation, y_title_installation), title_place, fill='black', font=font_bold)

    # 5. ДОБАВЛЕНИЕ QR-КОДА (если он есть)
    qr_y = 76
    if battery.qr_code and hasattr(battery.qr_code, 'path'):
        try:
            # Открываем существующий QR-код как изображение
            qr_img = Image.open(battery.qr_code.path)
            # Изменяем размер QR-кода, если нужно (например, 100x100 пикселей)
            qr_size = 168
            qr_img = qr_img.resize((qr_size, qr_size))
            # Вставляем QR-код в основное изображение (по центру)
            qr_x = 36
            img.paste(qr_img, (qr_x, qr_y))
            # qr_y = 76
        except FileNotFoundError:
            # Если файл QR не найден, добавляем текстовую заглушку
            draw.text((36, qr_y), "QR-код отсутствует", fill='red', font=font_regular)
            qr_y = 76

    # 6. ДОБАВЛЕНИЕ ДАННЫХ НА ИЗОБРАЖЕНИЕ
    # Пример: Добавляем заголовок
    title = f"АБ №{battery.battery_number}"
    bbox = draw.textbbox((0, 0), title, font=font_bold)
    text_width = bbox[2] - bbox[0]
    
    # Рассчитываем позицию для центрирования текста по ширине
    x_title = ((width_px) // 2 - text_width) // 2
    y_title = qr_y + qr_size + 10
    draw.text((x_title, y_title), title, fill='black', font=font_bold)

    # 7. ДОБАВЛЕНИЕ ОСТАЛЬНЫХ ПАРАМЕТРОВ АБ
    x_right = 250
    y = 20
    padding_bottom = 25
    
    # Тип: обычный текст + жирное значение
    draw_mixed_text(draw, [
        ("Тип: ", font_regular),
        (f"{ battery.battery_type.manufacturer } { battery.battery_type.battery_type_title }", font_bold)
    ], x_right, y)
    
    y += padding_bottom

    # S/N
    serial_number = battery.serial_parameters.serial_number if battery.serial_parameters else "Н/Д"
    draw_mixed_text(draw, [
        ("S/N: ", font_regular),
        (f"{ serial_number }", font_bold)
    ], x_right, y)
    
    y += padding_bottom
    
    # Дата изготовления
    draw_mixed_text(draw, [
        ("Дата изготовления:", font_regular),
    ], x_right, y)
    
    y += padding_bottom

    if battery.serial_parameters and battery.serial_parameters.manufacture_date:
        date_manufacter = battery.serial_parameters.manufacture_date.strftime('%d.%m.%Y')
    else:
        date_manufacter = "Н/Д"

    draw_mixed_text(draw, [
        (f"{ date_manufacter }", font_bold)
    ], x_right, y)
    
    y += padding_bottom

    # Дата измерения
    draw_mixed_text(draw, [
        ("Дата измерения:", font_regular),
    ], x_right, y)
    
    y += padding_bottom

    last_testing = testings_dbt12d.last()
    if last_testing and last_testing.testing_date:
        date_measure = last_testing.testing_date.strftime('%d.%m.%Y')
    else:
        date_measure = "Н/Д"

    draw_mixed_text(draw, [
        (f"{ date_measure }", font_bold)
    ], x_right, y)
    
    y += padding_bottom
    
    # SOH, SOC
    SOH = f"{ testings_dbt12d.last().SOH.to_integral_value() }%, " if last_testing and last_testing.SOH is not None else "Н/Д "
    SOC = f"{ testings_dbt12d.last().SOC.to_integral_value() }%" if last_testing and last_testing.SOC is not None else "Н/Д"

    draw_mixed_text(draw, [
        ("SOH: ", font_regular),
        (SOH, font_bold),
        ("SOC: ", font_regular),
        (SOC, font_bold)
    ], x_right, y)

    y += padding_bottom

    # Напряжение
    vol_text = f"{last_testing.VOL} В" if last_testing and last_testing.VOL is not None else "Н/Д"

    draw_mixed_text(draw, [
        ("Напряжение: ", font_regular),
        (vol_text, font_bold)
    ], x_right, y)

    y += padding_bottom

    # R ном
    R_nom = f"{ battery.battery_type.internal_resistance } мОм" if battery.battery_type and battery.battery_type.internal_resistance is not None else "Н/Д"

    draw_mixed_text(draw, [
        ("R ном: ", font_regular),
        (R_nom, font_bold)
    ], x_right, y)
    
    y += padding_bottom

    # R изм
    R_meas = f"{ testings_dbt12d.last().R } мОм" if last_testing and last_testing.R is not None else "Н/Д"

    draw_mixed_text(draw, [
        ("R изм: ", font_regular),
        (R_meas, font_bold)
    ], x_right, y)
    
    # 8. СОХРАНЕНИЕ ИЗОБРАЖЕНИЯ В БУФЕР И ОТПРАВКА КЛИЕНТУ
    # Сохраняем изображение в байтовый буфер
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Формируем HTTP-ответ с изображением
    response = HttpResponse(buffer, content_type='image/png')
    
    # Указываем браузеру, что это файл для скачивания, а не для показа
    filename = f"battery_label_{battery.battery_number}.png"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def draw_mixed_text(draw, text_parts, x, y, fill='black'):
    """
    Рисует текст с разными шрифтами в одной строке
    
    Параметры:
    - draw: объект ImageDraw
    - text_parts: список кортежей [(текст1, шрифт1), (текст2, шрифт2), ...]
    - x, y: начальные координаты
    - fill: цвет
    Возвращает: x-координату после последнего символа
    """
    current_x = x
    
    for text, font in text_parts:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_height = bbox[3] - bbox[0]
        
        # Для вертикального выравнивания вычисляем смещение по Y
        ascent, descent = font.getmetrics()
        y_pos = y + ascent  # Это базовая линия текста
        
        draw.text((current_x, y_pos), text, fill=fill, font=font)
        
        # Сдвигаем X для следующей части
        current_x += bbox[2] - bbox[0]
    
    return current_x