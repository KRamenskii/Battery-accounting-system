# management/commands/generate_qr_for_existing.py
from django.core.management.base import BaseCommand
from journal.models import Battery
from django.db import transaction

class Command(BaseCommand):
    help = 'Генерирует QR-коды для всех существующих батарей'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Количество батарей для обработки за раз'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        batteries = Battery.objects.all()
        total = batteries.count()
        
        self.stdout.write(f'Начинаем генерацию QR-кодов для {total} батарей...')
        
        for i in range(0, total, batch_size):
            batch = batteries[i:i + batch_size]
            with transaction.atomic():
                for battery in batch:
                    try:
                        battery.generate_qr_code(force_generate=True)
                        battery.save(update_fields=['qr_code', 'qr_data_hash'])
                        self.stdout.write(f'  Обработана батарея {battery.battery_number}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Ошибка с {battery.battery_number}: {str(e)}')
                        )
            
            self.stdout.write(f'Прогресс: {min(i + batch_size, total)}/{total}')
        
        self.stdout.write(self.style.SUCCESS('Готово!'))