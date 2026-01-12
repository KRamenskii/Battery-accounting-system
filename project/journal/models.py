import qrcode
import hashlib
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
import os

class InstallationLocation(models.Model):
    LOCATION_TYPES = [
        ('container', 'Шкаф'),
        ('virtual', 'Промежуточное место, путь'),
    ]

    location_title = models.CharField(
        max_length=255, 
        verbose_name="Название места установки"
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        default='container',
        verbose_name="Тип места установки"
    )
    system_title = models.CharField(
        max_length=255, 
        verbose_name="Описание", 
        null=True, 
        blank=True
    )
    system_name = models.CharField(
        max_length=255, 
        verbose_name="Название системы",
        null=True,
        blank=True
    )
    nominal_capacity = models.DecimalField(
        verbose_name="Номинальная емкость АБ, А⋅ч",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    battery_count = models.PositiveIntegerField(
        verbose_name="Количество АБ",
        default=0
    )
    parent_location = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_locations',
        verbose_name="Родительское место"
    )
    nesting_level = models.PositiveIntegerField(verbose_name="Уровень вложенности", default=0)

    class Meta:
        verbose_name = "Место установки"
        verbose_name_plural = "Места установки"
        constraints = [
            models.UniqueConstraint(
                fields=['location_title', 'location_type', 'system_name'],
                name='unique_installation_location'
            )
        ]

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        if self.parent_location:
            return f"{str(self.parent_location)} → {self.location_title}"
        return self.location_title
    
    def get_nesting_level(self):
        if self.parent_location is None:
            return 0
        return self.parent_location.get_nesting_level() + 1
    
    @property
    def is_container(self):
        """Проверка, является ли место контейнером (где стоят АБ)"""
        return self.location_type == 'container'

    def save(self, *args, **kwargs):
        # Вычисляем уровень вложенности перед сохранением
        self.nesting_level = self.get_nesting_level()
        
        # Автоматически заполняем поля для не-контейнеров
        if not self.is_container:
            self.nominal_capacity = None
            self.battery_count = 0
        
        super().save(*args, **kwargs)


class SerialParameters(models.Model):
    battery_type = models.ForeignKey(
        'battery_types.BatteryType',
        on_delete=models.CASCADE,
        verbose_name="Тип АБ"
    )
    serial_number = models.CharField(
        max_length=255, 
        verbose_name="Серийный номер",
        unique=True  # Глобально уникальный
    )
    manufacture_date = models.DateField(
        verbose_name="Дата изготовления"
    )

    class Meta:
        verbose_name = "Серийный параметр"
        verbose_name_plural = "Серийные параметры"

    def __str__(self):
        return f"{self.serial_number} ({self.battery_type.battery_type_title})"

    def full_representation(self):
        return f"Серийный номер {self.serial_number} для типа АБ: {self.battery_type.battery_type_title}"


class Battery(models.Model):
    battery_type = models.ForeignKey(
        'battery_types.BatteryType',
        on_delete=models.CASCADE,
        verbose_name="Тип АБ"
    )
    serial_parameters = models.ForeignKey(
        'SerialParameters',
        on_delete=models.PROTECT,
        verbose_name="Серийные параметры",
        null=True,
        blank=True
    )
    battery_number = models.CharField(
        max_length=255, 
        verbose_name="Номер АБ",
        unique=True
    )
    acceptance_date = models.DateField(
        verbose_name="Дата приемки", 
        null=True, 
        blank=True
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/batteries/',
        verbose_name="QR-код",
        null=True,
        blank=True,
        editable=False
    )
    qr_data_hash = models.CharField(
        max_length=64,
        verbose_name="Хэш данных QR",
        null=True,
        blank=True,
        editable=False,
        help_text="Для определения, нужно ли перегенерировать QR"
    )

    class Meta:
        verbose_name = "АБ"
        verbose_name_plural = "АБ"

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        serial_info = self.serial_parameters.serial_number if self.serial_parameters else "Н/Д"
        return f"АБ №{self.battery_number} ({self.battery_type.battery_type_title}, SN: {serial_info})"
    
    def get_qr_text(self):
        """Текст, который будет виден при сканировании"""
        return f"АБ №{self.battery_number} / {self.battery_type.manufacturer} {self.battery_type.battery_type_title}"
    
    def calculate_qr_hash(self):
        """Вычисляет хэш от текста QR-кода для отслеживания изменений"""
        text = self.get_qr_text()
        return hashlib.sha256(text.encode()).hexdigest()
    
    def generate_qr_code(self, force_generate=False):
        """
        Генерирует и сохраняет QR-код как изображение.
        QR пересоздаётся, если:
        - изменились данные
        - файл отсутствует
        - передан force_generate=True
        """

        current_hash = self.calculate_qr_hash()

        # Проверяем наличие файла
        file_exists = False
        if self.qr_code and self.qr_code.name:
            try:
                file_exists = os.path.exists(self.qr_code.path)
            except (ValueError, OSError):
                file_exists = False

        # Если всё актуально — выходим
        if (
            not force_generate
            and self.qr_data_hash == current_hash
            and file_exists
        ):
            return

        # ---------- Генерация QR ----------
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_qr_text())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # ---------- Удаляем старый файл ----------
        if file_exists:
            try:
                os.remove(self.qr_code.path)
            except OSError:
                pass  # файл могли удалить параллельно — не критично

        # ---------- Сохраняем новый ----------
        filename = f"battery_qr_{self.id}_{self.battery_number}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        self.qr_data_hash = current_hash
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической генерации QR-кода"""
        is_new = self.pk is None
        
        # Сначала сохраняем объект, чтобы получить ID
        super().save(*args, **kwargs)
        
        # Генерируем QR-код
        self.generate_qr_code()
        
        # Сохраняем снова, чтобы обновить qr_code и qr_data_hash
        super().save(update_fields=['qr_code', 'qr_data_hash'])


class BatteryInstallationHistory(models.Model):
    battery = models.ForeignKey(
        Battery, 
        on_delete=models.CASCADE, 
        verbose_name="АБ",
        related_name='installation_history'
    )
    installation_location = models.ForeignKey(
        InstallationLocation,
        on_delete=models.CASCADE,
        verbose_name="Место установки"
    )
    installation_date = models.DateField(
        verbose_name="Дата установки",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "История установки АБ"
        verbose_name_plural = "Истории установки АБ"
        ordering = ['-installation_date']

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        return f"{self.battery} установлен в {self.installation_location} на {self.installation_date}"


class TestingDBT12D(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="АБ")
    testing_date = models.DateField(verbose_name="Дата тестирования")
    SOH = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Состояние здоровья (SOH)")
    SOC = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Состояние заряда (SOC)")
    VOL = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Напряжение (VOL)")
    R = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сопротивление (R)")
    STD = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стандарт (STD)")
    CCA = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Холодный ток запуска (CCA)")

    class Meta:
        verbose_name = "Тестирование DBT12D"
        verbose_name_plural = "Тестирования DBT12D"

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        serial_info = self.battery.serial_parameters.serial_number if self.battery.serial_parameters else "Н/Д"
        return f"Тестирование DBT12D АБ №{self.battery.battery_number} ({self.battery.battery_type.battery_type_title}, SN: {serial_info})"


class TestingIC105(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="АБ")
    testing_date = models.DateField(verbose_name="Дата тестирования")
    SOH = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Состояние здоровья (SOH)")
    VOL = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Напряжение (VOL)")
    R = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сопротивление (R)")
    STD = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стандарт (STD)")
    CCA = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Холодный ток запуска (CCA)")

    class Meta:
        verbose_name = "Тестирование IC-105"
        verbose_name_plural = "Тестирования IC-105"

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        serial_info = self.battery.serial_parameters.serial_number if self.battery.serial_parameters else "Н/Д"
        return f"Тестирование IC105 АБ №{self.battery.battery_number} ({self.battery.battery_type.battery_type_title}, SN: {serial_info})"