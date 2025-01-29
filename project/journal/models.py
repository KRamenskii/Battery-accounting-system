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
        return self.location_title
    
    def get_nesting_level(self):
        if self.parent_location is None:
            return 0
        return self.parent_location.get_nesting_level() + 1

    def save(self, *args, **kwargs):
        # Вычисляем уровень вложенности перед сохранением
        self.nesting_level = self.get_nesting_level()
        super().save(*args, **kwargs)

class Battery(models.Model):
    battery_type = models.ForeignKey(
        'battery_types.BatteryType',
        on_delete=models.CASCADE,
        verbose_name="Тип АКБ"
    )
    serial_number = models.CharField(
        max_length=255, 
        verbose_name="Серийный номер"
    )
    battery_number = models.CharField(
        max_length=255, 
        verbose_name="Номер АКБ"
    )
    manufacture_date = models.DateField(verbose_name="Дата изготовления")
    acceptance_date = models.DateField(
        verbose_name="Дата приемки", 
        null=True, 
        blank=True
    )
    installation_date = models.DateField(
        verbose_name="Дата установки на оборудование", 
        null=True, 
        blank=True
    )
    installation_location = models.ManyToManyField(
        InstallationLocation,
        verbose_name="Места установки",
        related_name="batteries"
    )

    class Meta:
        verbose_name = "АКБ"
        verbose_name_plural = "АКБ"

    def __str__(self):
        return f"АКБ №{self.battery_number} ({self.battery_type.battery_type_title})"

class TestingDBT12D(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="АКБ")
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

class TestingIC105(models.Model):
    battery = models.ForeignKey(Battery, on_delete=models.CASCADE, verbose_name="АКБ")
    testing_date = models.DateField(verbose_name="Дата тестирования")
    SOH = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Состояние здоровья (SOH)")
    VOL = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Напряжение (VOL)")
    R = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сопротивление (R)")
    STD = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стандарт (STD)")
    CCA = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Холодный ток запуска (CCA)")

    class Meta:
        verbose_name = "Тестирование IC-105"
        verbose_name_plural = "Тестирования IC-105"