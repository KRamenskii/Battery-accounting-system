from django.shortcuts import render
from datetime import date, timedelta
from django.db.models import Max

from journal.models import Battery, BatteryInstallationHistory, TestingDBT12D, TestingIC105


def homepage(request):
    storage = "Б-143, Б-144 (C)"
    utilization = "Б-143, Б-144 (У)"

    # Получаем последнюю установку каждой АБ
    all_installations = (
        BatteryInstallationHistory.objects
        .select_related('installation_location')
        .order_by('battery_id', '-installation_date', '-id')
    )

    latest_by_battery = {}
    for record in all_installations:
        if record.battery_id not in latest_by_battery:
            latest_by_battery[record.battery_id] = record

    batteries_on_equipment = 0
    batteries_on_storage = 0
    batteries_utilized = 0
    batteries_need_check_equipment = 0
    batteries_need_check_storage = 0

    # Полгода назад
    six_months_ago = date.today() - timedelta(days=180)

    storage_batteries = []
    equipment_batteries = []

    for battery_id, record in latest_by_battery.items():
        location = record.installation_location.location_title.strip()

        if location == utilization:
            batteries_utilized += 1
        elif location == storage:
            batteries_on_storage += 1
            storage_batteries.append(record.battery)
            # Проверяем последнюю дату тестирования
            last_test_db = TestingDBT12D.objects.filter(battery_id=battery_id).aggregate(last=Max('testing_date'))['last']
            last_test_ic = TestingIC105.objects.filter(battery_id=battery_id).aggregate(last=Max('testing_date'))['last']

            # Берем наиболее позднюю из двух
            last_test = max(filter(None, [last_test_db, last_test_ic]), default=None)

            if last_test is None or last_test < six_months_ago:
                batteries_need_check_storage += 1
        else:
            batteries_on_equipment += 1
            equipment_batteries.append(record.battery)

            # Проверяем последнюю дату тестирования
            last_test_db = TestingDBT12D.objects.filter(battery_id=battery_id).aggregate(last=Max('testing_date'))['last']
            last_test_ic = TestingIC105.objects.filter(battery_id=battery_id).aggregate(last=Max('testing_date'))['last']

            # Берем наиболее позднюю из двух
            last_test = max(filter(None, [last_test_db, last_test_ic]), default=None)

            if last_test is None or last_test < six_months_ago:
                batteries_need_check_equipment += 1
    
    # Создание таблицы по емкости АБ на складе
    battery_capacity_table_on_storage = []
    battery_types = set(b.battery_type for b in storage_batteries)

    for bt in battery_types:
        batteries = [b for b in storage_batteries if b.battery_type == bt]
        total = len(batteries)
        low_mid = 0
        low = 0
        no_data = 0

        for battery in batteries:
            latest_test = (
                TestingDBT12D.objects
                .filter(battery=battery)
                .order_by('-testing_date')
                .first()
            )

            if latest_test is None:
                no_data += 1
                continue

            soh = float(latest_test.SOH)
            if soh < 50:
                low += 1
            elif soh < 80:
                low_mid += 1

        battery_capacity_table_on_storage.append({
            'type': bt.battery_type_title,
            'total': total,
            'mid_low': low_mid,
            'low': low,
            'no_data': no_data
        })

    # Создание таблицы по емкости АБ на оборудовании
    battery_capacity_table_on_equipment = []
    battery_types = set(b.battery_type for b in equipment_batteries)

    for bt in battery_types:
        batteries = [b for b in equipment_batteries if b.battery_type == bt]
        total = len(batteries)
        low_mid = 0
        low = 0
        no_data = 0

        for battery in batteries:
            latest_test = (
                TestingDBT12D.objects
                .filter(battery=battery)
                .order_by('-testing_date')
                .first()
            )

            if latest_test is None:
                no_data += 1
                continue

            soh = float(latest_test.SOH)
            if soh < 50:
                low += 1
            elif soh < 80:
                low_mid += 1

        battery_capacity_table_on_equipment.append({
            'type': bt.battery_type_title,
            'total': total,
            'mid_low': low_mid,
            'low': low,
            'no_data': no_data
        })

    context = {
        'total_batteries': Battery.objects.count(),
        'batteries_on_equipment': batteries_on_equipment,
        'batteries_on_storage': batteries_on_storage,
        'batteries_utilized': batteries_utilized,
        'batteries_need_check_equipment': batteries_need_check_equipment,
        'batteries_need_check_storage': batteries_need_check_storage,
        'battery_capacity_table_on_storage': battery_capacity_table_on_storage,
        'battery_capacity_table_on_equipment': battery_capacity_table_on_equipment,
    }

    return render(request, 'homepage/homepage.html', context)