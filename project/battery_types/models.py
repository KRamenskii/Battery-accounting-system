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
    elements_count = models.IntegerField(verbose_name = 'Количество элементов в АБ')
    lifespan = models.IntegerField(verbose_name = 'Срок службы, лет')
    nominal_capacity_20 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 20-ти часовом разряде',
        max_digits=10, 
        decimal_places=2
    )
    nominal_capacity_10 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 10-ти часовом разряде',
        max_digits=10, 
        decimal_places=2,
        help_text='Ввести 0 при отсутствии данных'
    )
    nominal_capacity_5 = models.DecimalField(
        verbose_name = 'Номинальная ёмкость при 5-ти часовом разряде',
        max_digits=10, 
        decimal_places=2,
        help_text='Ввести 0 при отсутствии данных'
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
    weight = models.DecimalField(
        verbose_name='Вес АБ, кг',
        max_digits=10,
        decimal_places=2,
        null=True,  # Разрешаем NULL для существующих записей
        blank=True  # Поле не обязательно для заполнения в формах
    )

    class Meta:
        verbose_name = 'Тип АБ'
        verbose_name_plural = 'Типы АБ'
        # Уникальность по комбинации производителя и модели
        constraints = [
            models.UniqueConstraint(
                fields=['manufacturer', 'battery_type_title'],
                name='unique_battery_type'
            )
        ]

    def __str__(self):
        return self.battery_type_title

    def full_representation(self):
        return f"АБ производителя {self.manufacturer}, тип: {self.battery_type_title}. Параметры: {self.nominal_voltage} В, {self.nominal_capacity_20} A⋅ч"