from django.contrib import admin
from django.utils.html import format_html
from .models import Service, Project, ProjectImage, Testimonial, TeamMember, StudioPage, HeroSlide, ContactSubmission


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'service_type', 'is_featured', 'order', 'created_at']
    list_filter = ['service_type', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_featured']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client_name', 'status', 'is_featured', 'order', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['title', 'client_name', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProjectImageInline]


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'order', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['project__title', 'caption']
    list_editable = ['order']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_company', 'rating', 'is_featured', 'order', 'created_at']
    list_filter = ['rating', 'is_featured', 'created_at']
    search_fields = ['client_name', 'client_company', 'testimonial_text']
    list_editable = ['order', 'is_featured', 'rating']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'title']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_featured']


@admin.register(StudioPage)
class StudioPageAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'hero_title', 'updated_at']
    list_filter = ['page_type', 'updated_at']
    search_fields = ['hero_title', 'hero_subtitle']


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'label', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('preview', 'title')
    ordering = ('order',)
    readonly_fields = ('preview_large',)
    fields = ('title', 'image', 'preview_large', 'alt_text', 'label', 'order', 'is_active')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:64px;border-radius:8px">', obj.image.url)
        return "-"

    def preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:340px;border-radius:12px">', obj.image.url)
        return "No image yet"
    preview_large.short_description = "Preview"


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'need', 'timeline', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'need', 'timeline']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
