# journal/management/commands/fix_all_qr.py
from django.core.management.base import BaseCommand
from journal.models import Battery
import os

class Command(BaseCommand):
    help = 'Исправляет QR-коды для всех АБ'
    
    def handle(self, *args, **options):
        total = Battery.objects.count()
        fixed = 0
        errors = 0
        
        for i, battery in enumerate(Battery.objects.all(), 1):
            self.stdout.write(f"[{i}/{total}] АБ №{battery.battery_number}...")
            
            try:
                # Сбрасываем поля чтобы гарантировать генерацию
                battery.qr_code = None
                battery.qr_data_hash = None
                battery.save()  # Вызовет generate_qr_code
                
                if battery.qr_code and battery.qr_code.name:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ QR создан"))
                    fixed += 1
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ QR не создался"))
                    errors += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Ошибка: {e}"))
                errors += 1
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"✅ Исправлено: {fixed}"))
        self.stdout.write(self.style.WARNING(f"⚠️  С ошибками: {errors}"))
        self.stdout.write(self.style.SUCCESS(f"📊 Всего обработано: {total}"))