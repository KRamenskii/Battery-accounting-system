from django.db import models

class InstallationLocation(models.Model):
    location_title = models.CharField(
        max_length=255, 
        verbose_name="Название места установки"
    )
    system_title = models.CharField(
        max_length=255, 
        verbose_name="Название системы", 
        null=True, 
        blank=True
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

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        if self.parent_location:
            return f"{str(self.parent_location)} ---> {self.location_title}"
        return self.location_title
    
    def get_nesting_level(self):
        if self.parent_location is None:
            return 0
        return self.parent_location.get_nesting_level() + 1

    def save(self, *args, **kwargs):
        # Вычисляем уровень вложенности перед сохранением
        self.nesting_level = self.get_nesting_level()
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

    class Meta:
        verbose_name = "АБ"
        verbose_name_plural = "АБ"

    def __str__(self):
        return self.full_representation()

    def full_representation(self):
        serial_info = self.serial_parameters.serial_number if self.serial_parameters else "Н/Д"
        return f"АБ №{self.battery_number} ({self.battery_type.battery_type_title}, SN: {serial_info})"


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