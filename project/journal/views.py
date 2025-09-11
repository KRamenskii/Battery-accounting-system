from django.core.paginator import Paginator
from django.db.models import Max, OuterRef, Subquery
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Battery, BatteryInstallationHistory, InstallationLocation, TestingDBT12D, TestingIC105
from .forms import InstallationLocationForm, TestingDBT12DForm, TestingIC105Form, BatteryForm, BatteryInstallationHistoryForm


class InstallationLocationCreateView(CreateView):
    model = InstallationLocation
    form_class = InstallationLocationForm
    template_name = 'journal/installation_location_create.html'

    def get_success_url(self):
        return reverse_lazy('installation_locations')

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
    success_url = reverse_lazy('installation_locations')
    context_object_name = 'installation_location_edit'


class InstallationLocationDeleteView(DeleteView):
    model = InstallationLocation
    template_name = 'journal/installation_location_confirm_delete.html'
    success_url = reverse_lazy('installation_locations')
    context_object_name = 'installation_location_confirm_delete'


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
    form_class = BatteryForm
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
        'location_id': location_id
    })