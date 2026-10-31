from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display, action
from unfold.contrib.filters.admin import RangeNumericFilter
from .models import Service, Project, ProjectImage, Testimonial, TeamMember, StudioPage, HeroSlide, ContactSubmission, JobApplication


# Custom Rich Text Widget
class RichTextWidget(forms.Widget):
    """Custom widget with formatting toolbar for rich text editing"""
    
    def render(self, name, value, attrs=None, renderer=None):
        widget_id = attrs.get('id', name) if attrs else name
        
        toolbar_html = f'''
        <div style="margin-bottom: 8px; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; background: #f8fafc;">
            <button type="button" onclick="insertTag('{widget_id}', '<b>', '</b>')" style="padding: 4px 8px; margin-right: 4px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer;"><b>B</b></button>
            <button type="button" onclick="insertTag('{widget_id}', '<i>', '</i>')" style="padding: 4px 8px; margin-right: 4px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer;"><i>I</i></button>
            <button type="button" onclick="insertTag('{widget_id}', '<u>', '</u>')" style="padding: 4px 8px; margin-right: 4px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer;"><u>U</u></button>
            <button type="button" onclick="insertTag('{widget_id}', '<p>', '</p>')" style="padding: 4px 8px; margin-right: 4px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer;">P</button>
            <button type="button" onclick="insertTag('{widget_id}', '<br>', '')" style="padding: 4px 8px; margin-right: 4px; border: 1px solid #cbd5e1; border-radius: 4px; background: white; cursor: pointer;">BR</button>
        </div>
        '''
        
        textarea_html = f'<textarea id="{widget_id}" name="{name}" rows="12" style="width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-family: monospace;">{value or ""}</textarea>'
        
        js_html = f'''
        <script>
        function insertTag(id, openTag, closeTag) {{
            const textarea = document.getElementById(id);
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = textarea.value;
            const before = text.substring(0, start);
            const selection = text.substring(start, end);
            const after = text.substring(end);
            textarea.value = before + openTag + selection + closeTag + after;
            textarea.focus();
            textarea.selectionStart = textarea.selectionEnd = start + openTag.length + selection.length;
        }}
        </script>
        '''
        
        return format_html('{}{}{}', toolbar_html, textarea_html, js_html)


# Lucide Icon Choices
LUCIDE_ICONS = [
    ('briefcase', 'Business'),
    ('code', 'Code'),
    ('smartphone', 'Mobile'),
    ('cpu', 'AI/Machine Learning'),
    ('database', 'Database'),
    ('cloud', 'Cloud'),
    ('message-square', 'Consulting'),
    ('palette', 'Design'),
    ('globe', 'Web'),
    ('server', 'Server'),
    ('layers', 'ERP'),
    ('zap', 'Performance'),
    ('shield', 'Security'),
    ('settings', 'Settings'),
    ('tool', 'Tools'),
]


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ['service_icon', 'title', 'service_type_badge', 'is_featured', 'is_featured_badge', 'order', 'created_at']
    list_filter = ['service_type', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    
    # Custom actions
    actions = ['mark_featured', 'unmark_featured']
    
    @action(description="⭐ Mark as Featured")
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} services marked as featured.", messages.SUCCESS)
    
    @action(description="☆ Remove Featured")
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} services removed from featured.", messages.SUCCESS)
    
    @display(description="Icon")
    def service_icon(self, obj):
        if obj.icon:
            return format_html(
                '<div class="flex items-center gap-2"><span class="text-2xl">{}</span></div>',
                obj.icon
            )
        return "-"
    
    @display(description="Type")
    def service_type_badge(self, obj):
        colors = {
            'WEB': 'bg-blue-100 text-blue-700',
            'MOBILE': 'bg-purple-100 text-purple-700',
            'AI': 'bg-pink-100 text-pink-700',
            'ERP': 'bg-amber-100 text-amber-700',
            'CLOUD': 'bg-cyan-100 text-cyan-700',
            'CONSULTING': 'bg-green-100 text-green-700',
            'DESIGN': 'bg-rose-100 text-rose-700',
            'OTHER': 'bg-gray-100 text-gray-700',
        }
        color_class = colors.get(obj.service_type, 'bg-gray-100 text-gray-700')
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold {}">{}</span>',
            color_class,
            obj.get_service_type_display()
        )
    
    @display(description="Featured")
    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">⭐ Featured</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500">Standard</span>'
        )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'icon':
            kwargs['widget'] = forms.Select(choices=LUCIDE_ICONS)
        return super().formfield_for_dbfield(request, db_field, **kwargs)
    
    fieldsets = (
        (_('📋 Service Details'), {
            'fields': ('title', 'slug', 'service_type', 'icon'),
            "classes": ("tab-content",),
        }),
        (_('📝 Content'), {
            'fields': ('description', 'features'),
            "classes": ("tab-content",),
        }),
        (_('🖼️ Media'), {
            'fields': ('thumbnail',),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Settings'), {
            'fields': (('is_featured', 'order'),),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            "classes": ("collapse",),
        }),
    )


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    tab = True  # CRITICAL: Enables tabbed interface
    fields = ('image_preview', 'caption', 'order')
    readonly_fields = ('image_preview',)
    
    @display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="h-16 w-auto rounded border border-gray-200 shadow-sm" />',
                obj.image.url
            )
        return "-"


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['thumbnail_preview', 'title', 'client_name', 'status_badge', 'is_featured', 'is_featured_badge', 'order', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['title', 'client_name', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['order', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProjectImageInline]
    
    # Custom actions
    actions = ['mark_completed', 'mark_in_progress', 'toggle_featured']
    
    @action(description="✅ Mark as Completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f"{updated} projects marked as completed.", messages.SUCCESS)
    
    @action(description="🔄 Mark as In Progress")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f"{updated} projects marked as in progress.", messages.SUCCESS)
    
    @action(description="⭐ Toggle Featured")
    def toggle_featured(self, request, queryset):
        for project in queryset:
            project.is_featured = not project.is_featured
            project.save()
        self.message_user(request, f"Featured status toggled for {queryset.count()} projects.", messages.SUCCESS)
    
    @display(description="Thumbnail")
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" class="h-12 w-auto rounded border border-gray-200 shadow-sm" />',
                obj.thumbnail.url
            )
        return "-"
    
    @display(description="Status")
    def status_badge(self, obj):
        colors = {
            'COMPLETED': 'bg-green-100 text-green-700',
            'IN_PROGRESS': 'bg-blue-100 text-blue-700',
            'COMING_SOON': 'bg-purple-100 text-purple-700',
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-700')
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold {}">{}</span>',
            color_class,
            obj.get_status_display()
        )
    
    @display(description="Featured")
    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">⭐ Featured</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500">Standard</span>'
        )
    
    fieldsets = (
        (_('📋 Project Info'), {
            'fields': ('title', 'slug', 'client_name', 'short_description'),
            "classes": ("tab-content",),
        }),
        (_('📝 Full Description'), {
            'fields': ('full_description', 'technologies'),
            "classes": ("tab-content",),
        }),
        (_('🔗 Links'), {
            'fields': ('project_url', 'github_url'),
            "classes": ("tab-content",),
        }),
        (_('🖼️ Media'), {
            'fields': ('thumbnail', 'cover_image'),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Settings'), {
            'fields': (('status', 'is_featured'), 'completion_date', 'order'),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            "classes": ("collapse",),
        }),
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(ModelAdmin):
    list_display = ['image_preview', 'project', 'caption', 'order', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['project__title', 'caption']
    list_editable = ['order']
    
    @display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="h-16 w-auto rounded border border-gray-200 shadow-sm" />',
                obj.image.url
            )
        return "-"


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['avatar_preview', 'client_name', 'client_company', 'rating', 'rating_stars', 'is_featured', 'is_featured_badge', 'order', 'created_at']
    list_filter = ['rating', 'is_featured', 'created_at']
    search_fields = ['client_name', 'client_company', 'testimonial_text']
    list_editable = ['order', 'is_featured', 'rating']
    
    # Custom actions
    actions = ['mark_featured', 'unmark_featured']
    
    @action(description="⭐ Mark as Featured")
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} testimonials marked as featured.", messages.SUCCESS)
    
    @action(description="☆ Remove Featured")
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} testimonials removed from featured.", messages.SUCCESS)
    
    @display(description="Avatar")
    def avatar_preview(self, obj):
        if obj.client_avatar:
            return format_html(
                '<img src="{}" class="h-10 w-10 rounded-full border border-gray-200 shadow-sm" />',
                obj.client_avatar.url
            )
        return format_html(
            '<div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">{}</div>',
            obj.client_name[:1].upper()
        )
    
    @display(description="Rating")
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html(
            '<span class="text-yellow-500">{}</span>',
            stars
        )
    
    @display(description="Featured")
    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">⭐ Featured</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500">Standard</span>'
        )
    
    fieldsets = (
        (_('👤 Client Info'), {
            'fields': ('client_name', 'client_company', 'client_position', 'client_avatar'),
            "classes": ("tab-content",),
        }),
        (_('💬 Testimonial'), {
            'fields': ('testimonial_text', 'rating', 'project_link'),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Settings'), {
            'fields': (('is_featured', 'order'),),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            "classes": ("collapse",),
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ['photo_preview', 'name', 'title', 'is_featured', 'is_featured_badge', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'title']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_featured']
    
    # Custom actions
    actions = ['mark_featured', 'unmark_featured']
    
    @action(description="⭐ Mark as Featured")
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} team members marked as featured.", messages.SUCCESS)
    
    @action(description="☆ Remove Featured")
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} team members removed from featured.", messages.SUCCESS)
    
    @display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" class="h-12 w-12 rounded-full border border-gray-200 shadow-sm" />',
                obj.photo.url
            )
        return format_html(
            '<div class="h-12 w-12 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-sm">{}</div>',
            obj.name[:1].upper()
        )
    
    @display(description="Featured")
    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">⭐ Featured</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500">Standard</span>'
        )
    
    fieldsets = (
        (_('👤 Profile'), {
            'fields': ('name', 'slug', 'title', 'photo'),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Settings'), {
            'fields': (('is_featured', 'order'),),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            "classes": ("collapse",),
        }),
    )


@admin.register(StudioPage)
class StudioPageAdmin(ModelAdmin):
    list_display = ['page_type_badge', 'hero_title', 'updated_at']
    list_filter = ['page_type', 'updated_at']
    search_fields = ['hero_title', 'hero_subtitle']
    
    @display(description="Page")
    def page_type_badge(self, obj):
        colors = {
            'HOME': 'bg-blue-100 text-blue-700',
            'ABOUT': 'bg-purple-100 text-purple-700',
            'CONTACT': 'bg-green-100 text-green-700',
            'TEAM': 'bg-amber-100 text-amber-700',
        }
        color_class = colors.get(obj.page_type, 'bg-gray-100 text-gray-700')
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold {}">{}</span>',
            color_class,
            obj.get_page_type_display()
        )
    
    fieldsets = (
        (_('📄 Page Type'), {
            'fields': ('page_type',),
            "classes": ("tab-content",),
        }),
        (_('🎯 Hero Section'), {
            'fields': ('hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_link'),
            "classes": ("tab-content",),
        }),
        (_('🔍 SEO'), {
            'fields': ('meta_title', 'meta_description'),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('updated_at',),
            "classes": ("collapse",),
        }),
    )


@admin.register(HeroSlide)
class HeroSlideAdmin(ModelAdmin):
    list_display = ('preview', 'title', 'label', 'order', 'is_active', 'is_active_badge')
    list_editable = ('order', 'is_active')
    list_display_links = ('preview', 'title')
    ordering = ('order',)
    readonly_fields = ('preview_large',)
    fields = ('title', 'image', 'preview_large', 'alt_text', 'label', 'order', 'is_active')
    
    # Custom actions
    actions = ['activate_slides', 'deactivate_slides']
    
    @action(description="🟢 Activate Selected")
    def activate_slides(self, request, queryset):
        count = queryset.count()
        active_count = HeroSlide.objects.filter(is_active=True).exclude(pk__in=queryset).count()
        if active_count + count > HeroSlide.MAX_ACTIVE:
            self.message_user(request, f"Cannot activate: Only {HeroSlide.MAX_ACTIVE} slides can be active at once.", messages.ERROR)
        else:
            queryset.update(is_active=True)
            self.message_user(request, f"{count} slides activated.", messages.SUCCESS)
    
    @action(description="🔴 Deactivate Selected")
    def deactivate_slides(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} slides deactivated.", messages.SUCCESS)
    
    @display(description="Preview")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="h-16 w-auto rounded border border-gray-200 shadow-sm" />',
                obj.image.url
            )
        return "-"
    
    @display(description="Active")
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">🟢 Active</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-500">🔴 Inactive</span>'
        )
    
    def preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="max-h-96 rounded-lg shadow-lg" />',
                obj.image.url
            )
        return "No image yet"
    preview_large.short_description = "Preview"


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ModelAdmin):
    list_display = ['name', 'email', 'need', 'timeline', 'is_read', 'is_read_badge', 'created_at']
    list_filter = ['is_read', 'created_at', 'need', 'timeline']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    
    # Custom actions
    actions = ['mark_as_read', 'mark_as_unread']
    
    @action(description="📧 Mark as Read")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} submissions marked as read.", messages.SUCCESS)
    
    @action(description="📨 Mark as Unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} submissions marked as unread.", messages.SUCCESS)
    
    @display(description="Status")
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">✓ Read</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">📨 New</span>'
        )
    
    fieldsets = (
        (_('👤 Contact Info'), {
            'fields': ('name', 'email'),
            "classes": ("tab-content",),
        }),
        (_('📋 Project Details'), {
            'fields': ('need', 'timeline'),
            "classes": ("tab-content",),
        }),
        (_('💬 Message'), {
            'fields': ('message',),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Status'), {
            'fields': ('is_read',),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at',),
            "classes": ("collapse",),
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(ModelAdmin):
    list_display = ['name', 'email', 'role_badge', 'is_reviewed', 'is_reviewed_badge', 'created_at']
    list_filter = ['role', 'is_reviewed', 'created_at']
    search_fields = ['name', 'email', 'cover_letter']
    list_editable = ['is_reviewed']
    readonly_fields = ['created_at']
    
    # Custom actions
    actions = ['mark_as_reviewed', 'mark_as_pending']
    
    @action(description="✅ Mark as Reviewed")
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(is_reviewed=True)
        self.message_user(request, f"{updated} applications marked as reviewed.", messages.SUCCESS)
    
    @action(description="⏳ Mark as Pending")
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(is_reviewed=False)
        self.message_user(request, f"{updated} applications marked as pending.", messages.SUCCESS)
    
    @display(description="Role")
    def role_badge(self, obj):
        colors = {
            'FRONTEND': 'bg-blue-100 text-blue-700',
            'BACKEND': 'bg-green-100 text-green-700',
            'FULLSTACK': 'bg-purple-100 text-purple-700',
            'MOBILE': 'bg-pink-100 text-pink-700',
            'UI_UX': 'bg-rose-100 text-rose-700',
            'PRODUCT': 'bg-amber-100 text-amber-700',
            'DEVOPS': 'bg-cyan-100 text-cyan-700',
            'DATA': 'bg-indigo-100 text-indigo-700',
            'OTHER': 'bg-gray-100 text-gray-700',
        }
        color_class = colors.get(obj.role, 'bg-gray-100 text-gray-700')
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold {}">{}</span>',
            color_class,
            obj.get_role_display()
        )
    
    @display(description="Status")
    def is_reviewed_badge(self, obj):
        if obj.is_reviewed:
            return format_html(
                '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">✓ Reviewed</span>'
            )
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700">⏳ Pending</span>'
        )
    
    fieldsets = (
        (_('👤 Applicant Info'), {
            'fields': ('name', 'email', 'phone'),
            "classes": ("tab-content",),
        }),
        (_('💼 Role & Profile'), {
            'fields': ('role', 'corelink_profile', 'github', 'linkedin', 'portfolio'),
            "classes": ("tab-content",),
        }),
        (_('📝 Cover Letter'), {
            'fields': ('cover_letter',),
            "classes": ("tab-content",),
        }),
        (_('📎 Resume'), {
            'fields': ('resume',),
            "classes": ("tab-content",),
        }),
        (_('⚙️ Status'), {
            'fields': ('is_reviewed',),
            "classes": ("tab-content",),
        }),
        (_('📅 Timestamps'), {
            'fields': ('created_at',),
            "classes": ("collapse",),
        }),
    )
