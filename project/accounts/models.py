from django.contrib.auth.models import AbstractUser
from django.db import models

# Модель роли
class Role(models.Model):
    role_title = models.CharField(max_length=20)

    def __str__(self):
        return self.role_title

# Модель организации
class Organization(models.Model):
    organization_title = models.CharField(max_length=255)

    def __str__(self):
        return self.organization_title

# Модель службы
class Department(models.Model):
    department_title = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.department_title

# Модель участка
class SubDepartment(models.Model):
    subdepartment_title = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.subdepartment_title

# Модель должности
class Job(models.Model):
    job_title = models.CharField(max_length=255)

    def __str__(self):
        return self.job_title

# Модель Пользователя
class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    user_name = models.CharField(max_length=20)
    sur_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    first_phone_number = models.CharField(max_length=14)
    second_phone_number = models.CharField(max_length=4, blank=True, null=True)

    # Связь с организацией, службой и участком
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    subdepartment = models.ForeignKey(SubDepartment, on_delete=models.SET_NULL, null=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.sur_name} {self.user_name}"