from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import redirect


# Core admin configuration using Unfold
# This file serves as a base for custom admin patterns


class CoreLinkModelAdmin(ModelAdmin):
    """
    Base ModelAdmin class with CoreLink branding and common patterns.
    All admin classes should inherit from this for consistent styling.
    """
    pass


# Example custom action pattern (can be used across apps)
@admin.action(description="🟢 Mark as Active")
def mark_active(self, request, queryset):
    """Bulk action to mark items as active"""
    updated = queryset.update(is_active=True)
    self.message_user(request, f"{updated} items marked as active.", messages.SUCCESS)


@admin.action(description="🔴 Mark as Inactive")
def mark_inactive(self, request, queryset):
    """Bulk action to mark items as inactive"""
    updated = queryset.update(is_active=False)
    self.message_user(request, f"{updated} items marked as inactive.", messages.SUCCESS)


# Register custom actions for use in other admin classes
class CoreLinkAdminSite(admin.AdminSite):
    """Custom admin site with CoreLink branding"""
    site_header = "CORE.LINK STUDIO"
    site_title = "Corelink Studio Admin"
    index_title = "Welcome to Corelink Studio Administration"
    
    def get_app_list(self, request, app_label=None):
        """
        Override to customize app list ordering and grouping
        """
        app_list = super().get_app_list(request, app_label)
        
        # Reorder apps to show Studio first
        studio_app = next((app for app in app_list if app['app_label'] == 'studio'), None)
        if studio_app:
            app_list.remove(studio_app)
            app_list.insert(0, studio_app)
        
        return app_list
