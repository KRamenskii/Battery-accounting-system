from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Role, CustomUser, Organization, Department, SubDepartment, Job, ErrorType, ErrorStatus, ErrorReport

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'email', 'sur_name', 'user_name', 'last_name',
            'first_phone_number', 'second_phone_number',
            'organization', 'department', 'subdepartment', 'job', 'role'
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('username', 'email', 'role', 'is_staff', 'sur_name', 'user_name')
    search_fields = ('username', 'email', 'sur_name', 'user_name')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'password')
        }),
        ('Персональные данные', {
            'fields': (
                'sur_name', 'user_name', 'last_name', 'email',
                'first_phone_number', 'second_phone_number'
            )
        }),
        ('Организация', {
            'fields': ('organization', 'department', 'subdepartment', 'job', 'role')
        }),
        ('Права доступа', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        ('Создание пользователя', {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'sur_name', 'user_name', 'last_name', 'email',
                'first_phone_number', 'second_phone_number',
                'organization', 'department', 'subdepartment', 'job', 'role',
                'is_staff', 'is_active'
            )
        }),
    )

    ordering = ('username',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_title')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_title')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'department_title', 'organization')
    list_filter = ('organization',)

@admin.register(SubDepartment)
class SubDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subdepartment_title', 'department')
    list_filter = ('department',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_title')

@admin.register(ErrorType)
class ErrorTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(ErrorStatus)
class ErrorStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(ErrorReport)
class ErrorReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "error_type", "status", "created_at", "updated_at")
    list_filter = ("error_type", "status", "created_at")
    search_fields = ("description", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")