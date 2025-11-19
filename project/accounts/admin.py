from django.contrib import admin
from .models import Role, CustomUser, Organization, Department, SubDepartment, Job, ErrorType, ErrorStatus, ErrorReport

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_title')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_active')

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