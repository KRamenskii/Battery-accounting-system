import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Restore PostgreSQL database from backup'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Name of the backup file to restore'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        full_path = os.path.join(backup_dir, backup_file)
        
        if not os.path.exists(full_path):
            self.stdout.write(self.style.ERROR(f'✗ Backup file not found: {full_path}'))
            return
        
        db_settings = settings.DATABASES['default']
        
        # Команда для восстановления
        cmd = [
            'psql',
            '-h', db_settings.get('HOST', 'localhost'),
            '-p', str(db_settings.get('PORT', '5432')),
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', full_path
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        self.stdout.write(f"Restoring from backup: {full_path}")
        
        try:
            result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            self.stdout.write(self.style.SUCCESS('✓ Database successfully restored'))
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'✗ Restore failed with error: {e.stderr}'))