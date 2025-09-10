import os
import subprocess
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'PostgreSQL database backup command'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compress', 
            action='store_true',
            help='Create compressed backup'
        )
        parser.add_argument(
            '--list',
            action='store_true', 
            help='List existing backups'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_backups()
            return
            
        self.create_backup(options['compress'])

    def create_backup(self, compress=False):
        """Create database backup"""
        db_settings = settings.DATABASES['default']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        # Создаем директорию если не существует
        os.makedirs(backup_dir, exist_ok=True)
        
        # Генерируем имя файла
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
        
        if compress:
            backup_file += '.gz'
        
        # Команда для PostgreSQL
        cmd = [
            'pg_dump',
            '-h', db_settings.get('HOST', 'localhost'),
            '-p', str(db_settings.get('PORT', '5432')),
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', backup_file
        ]
        
        # Добавляем сжатие если нужно
        if compress:
            cmd.insert(1, '--compress=9')
        
        # Устанавливаем переменные окружения для пароля
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        self.stdout.write(f"Creating backup to: {backup_file}")
        
        try:
            result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Backup successfully created: {backup_file}')
            )
            file_size = os.path.getsize(backup_file)
            self.stdout.write(f"Backup size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Backup failed with error: {e.stderr}')
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('✗ pg_dump not found. Please install PostgreSQL client tools')
            )

    def list_backups(self):
        """List existing backups"""
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        if not os.path.exists(backup_dir):
            self.stdout.write("No backups directory found")
            return
            
        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith('backup_') and (file.endswith('.sql') or file.endswith('.sql.gz')):
                file_path = os.path.join(backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                backups.append((file, file_size, file_time))
        
        if not backups:
            self.stdout.write("No backups found")
            return
            
        backups.sort(key=lambda x: x[2], reverse=True)
        
        self.stdout.write("Existing backups:")
        for file, size, time in backups:
            self.stdout.write(f"  {file} - {size} bytes - {time.strftime('%Y-%m-%d %H:%M:%S')}")