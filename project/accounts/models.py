from django.contrib.auth.models import AbstractUser
from django.db import models

# Модель роли
class Role(models.Model):
    role_title = models.CharField(
        verbose_name='Название роли',
        max_length=20
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.role_title

# Модель организации
class Organization(models.Model):
    organization_title = models.CharField(
        verbose_name='Название организации',
        max_length=255
    )

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.organization_title

# Модель службы
class Department(models.Model):
    department_title = models.CharField(
        verbose_name='Название службы',
        max_length=255
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        verbose_name='Организация',
    )

    class Meta:
        verbose_name = 'Служба'
        verbose_name_plural = 'Службы'

    def __str__(self):
        return self.department_title

# Модель участка
class SubDepartment(models.Model):
    subdepartment_title = models.CharField(
        verbose_name='Название участка',
        max_length=255
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='Служба',
    )

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'

    def __str__(self):
        return self.subdepartment_title

# Модель должности
class Job(models.Model):
    job_title = models.CharField(
        verbose_name='Название должности',
        max_length=255
    )

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.job_title

# Модель Пользователя
class CustomUser(AbstractUser):
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Роль пользователя'
    )
    user_name = models.CharField(
        verbose_name='Имя',
        max_length=20
    )
    sur_name = models.CharField(
        verbose_name='Фамилия',
        max_length=20
    )
    last_name = models.CharField(
        verbose_name='Отчество',
        max_length=20, 
        blank=True, 
        null=True
    )
    email = models.EmailField(unique=True)
    first_phone_number = models.CharField(
        verbose_name='Сотовый номер телефона',
        max_length=14
    )
    second_phone_number = models.CharField(
        verbose_name='Домашний номер телефона',
        max_length=4, 
        blank=True, 
        null=True
    )

    # Связь с организацией, службой и участком
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Организация',
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Служба',
    )
    subdepartment = models.ForeignKey(
        SubDepartment, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Участок',
    )
    job = models.ForeignKey(
        Job, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Должность',
    )

    def __str__(self):
        return f"{self.sur_name} {self.user_name}"