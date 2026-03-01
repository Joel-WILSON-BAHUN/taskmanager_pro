from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Tenant, User, Project, Task


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation']
    search_fields = ['nom']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'tenant', 'role', 'is_active']
    list_filter = ['tenant', 'role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations TaskManager', {'fields': ('tenant', 'role', 'bio')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations TaskManager', {'fields': ('tenant', 'role')}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['nom', 'tenant', 'date_debut', 'date_fin', 'created_by']
    list_filter = ['tenant']
    search_fields = ['nom', 'tenant__nom']
    filter_horizontal = ['membres']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['titre', 'projet', 'tenant', 'assigne_a', 'statut', 'priorite', 'date_limite']
    list_filter = ['tenant', 'statut', 'priorite', 'projet']
    search_fields = ['titre', 'projet__nom']
    list_editable = ['statut', 'priorite']
