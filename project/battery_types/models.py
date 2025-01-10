from django.db import models

class BatteryType(models.Model):
    manufacturer = models.CharField(
        verbose_name = 'Производитель',
        max_length=255
    )
    battery_type_title = models.CharField(
        verbose_name = 'Модель',
        max_length=255
    )
    nominal_voltage = models.DecimalField(
        verbose_name = 'Номинальное напряжение, В',
        max_digits=10,
        decimal_places=2
    )
    elements_count = models.IntegerField(verbose_name = 'Количество элементов в АКБ')
    lifespan = models.IntegerField(verbose_name = 'Скрок службы, лет')
    nominal_capacity_20 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 20-ти часовом разряде',
        max_digits=10, 
        decimal_places=2
    )
    nominal_capacity_10 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 10-ти часовом разряде',
        max_digits=10, 
        decimal_places=2
    )
    nominal_capacity_5 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 5-ти часовом разряде',
        max_digits=10, 
        decimal_places=2
    )
    self_discharge = models.DecimalField(
        verbose_name = 'Саморазряд, %',
        max_digits=10, 
        decimal_places=2
    )
    internal_resistance = models.DecimalField(
        verbose_name = 'Внутреннее сопротивление, мОм',
        max_digits=10, 
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Тип АКБ'
        verbose_name_plural = 'Типы АКБ'

    def __str__(self):
        return self.battery_type_title