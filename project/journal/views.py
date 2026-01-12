from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import Battery, BatteryInstallationHistory, InstallationLocation, TestingDBT12D, TestingIC105
from .forms import InstallationLocationForm, TestingDBT12DForm, TestingIC105Form, BatteryForm, BatteryInstallationHistoryForm, BatteryUpdateForm


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
        # Используем pk вместо battery_id
        return reverse_lazy('battery_detail', kwargs={'pk': self.object.battery.id})


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
        # Используем pk вместо battery_id
        return reverse_lazy('battery_detail', kwargs={'pk': self.object.battery.id})


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
        initial['battery'] = battery
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        battery_id = self.kwargs.get('battery_id')
        kwargs['battery'] = get_object_or_404(Battery, id=battery_id)  # Передаем аккумулятор в форму
        return kwargs

    def get_success_url(self):
        return reverse_lazy('battery_detail', kwargs={'pk': self.object.battery.id})


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
    """Отображение страницы журнала с учетом фильтрации по местоположению и типу АБ"""
    #  Получаем параметр фильтрации по типу из GET-запроса
    battery_type_id = request.GET.get('type')

    last_installation_subquery = BatteryInstallationHistory.objects.filter(
        battery=OuterRef("pk")
    ).order_by("-installation_date").values("installation_location_id")[:1]

    batteries = Battery.objects.annotate(
        last_location=Subquery(last_installation_subquery)
    )

    # Применяем фильтр по типу АБ, если он задан
    if battery_type_id and battery_type_id != 'all':
        batteries = batteries.filter(battery_type_id=battery_type_id)

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
        parent_locations = get_parent_locations(selected_location)  # Получаем родителей
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

    latest_soh_subquery = TestingDBT12D.objects.filter(
        battery=OuterRef('pk')
    ).order_by('-testing_date').values('SOH')[:1]

    latest_vol_subquery = TestingDBT12D.objects.filter(
        battery=OuterRef('pk')
    ).order_by('-testing_date').values('VOL')[:1]

    batteries = batteries.annotate(
        last_testing_date=Subquery(latest_test_subquery),
        last_soh=Subquery(latest_soh_subquery),
        last_vol=Subquery(latest_vol_subquery)
    )

    # Получаем только те типы АБ, которые есть в отфильтрованном наборе
    battery_types = batteries.order_by('battery_type__battery_type_title') \
                           .values_list('battery_type__id', 'battery_type__battery_type_title') \
                           .distinct()

    journal_data = [
        {
            "index": index,
            "installation_location": InstallationLocation.objects.get(id=battery.last_location).location_title
            if battery.last_location else "Не установлено",
            "battery_number": battery.battery_number,
            "battery_type": battery.battery_type.battery_type_title,
            "testing_date": battery.last_testing_date or "Нет данных",
            "soh": battery.last_soh or "Нет данных",
            "vol": battery.last_vol,
            "battery_id": battery.id
        }
        for index, battery in enumerate(batteries, start=1)
    ]

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
        "selected_battery_type": int(battery_type_id) if battery_type_id and battery_type_id != 'all' else None
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
    installation_location = installation_locations.last().installation_location

    # Получаем все места установки для выпадающего списка
    all_installation_locations = InstallationLocation.objects.all()
    
    installations_path = [
        (location, get_parent_locations(location.installation_location) + [location.installation_location])
        for location in installation_locations
    ]

    return render(request, 'journal/battery_detail.html', {
        'battery': battery,
        'testings_dbt12d': testings_dbt12d,
        'testings_ic105': testings_ic105,
        'model_dbt12d': 'DBT12D',
        'model_ic105': 'IC105',
        'installation_locations': installation_locations,
        'installations_path': installations_path,
        'location_id': location_id,
        'all_installation_locations': all_installation_locations,
        'installation_location': installation_location
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
    

# Редавтирование результатов тестирования АБ и истории мест установок
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