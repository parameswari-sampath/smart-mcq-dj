from django.contrib import admin
from .models import Organization, Profile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'organization', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
