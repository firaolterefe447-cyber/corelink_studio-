import csv
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.http import HttpResponse
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display, action
from unfold.contrib.filters.admin import RangeNumericFilter
from .models import Company, ContactPerson, PhoneNumber, SocialLink, CommunicationLog, Opportunity


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class PhoneNumberInline(TabularInline):
    """Inline for phone numbers in company/contact admin."""
    model = PhoneNumber
    extra = 1
    fields = ['number', 'phone_type', 'is_primary', 'is_verified']
    verbose_name = _("Phone Number")
    verbose_name_plural = _("Phone Numbers")


class SocialLinkInline(TabularInline):
    """Inline for social links in company admin."""
    model = SocialLink
    extra = 1
    fields = ['platform', 'url', 'is_primary']
    verbose_name = _("Social Link")
    verbose_name_plural = _("Social Links")


class ContactPersonInline(StackedInline):
    """Inline for contact persons in company admin."""
    model = ContactPerson
    extra = 0
    fields = ['name', 'role', 'telegram_handle', 'is_primary']
    verbose_name = _("Contact Person")
    verbose_name_plural = _("Contact People")
    classes = ('tab-contacts',)


class CommunicationLogInline(TabularInline):
    """Inline for communication logs in company admin."""
    model = CommunicationLog
    extra = 0
    fields = ['date', 'method', 'outcome', 'next_action_date']
    readonly_fields = ['date']
    can_delete = True
    verbose_name = _("Communication")
    verbose_name_plural = _("Communications")
    classes = ('tab-communications',)


class OpportunityInline(TabularInline):
    """Inline for opportunities in company admin."""
    model = Opportunity
    extra = 0
    fields = ['title', 'opportunity_type', 'status', 'estimated_value', 'probability', 'expected_close_date']
    readonly_fields = ['created_at']
    can_delete = True
    verbose_name = _("Opportunity")
    verbose_name_plural = _("Opportunities")
    classes = ('tab-opportunities',)


# ============================================================================
# MAIN ADMIN CLASSES
# ============================================================================

@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    """Admin interface for Company model with beautiful UI."""
    
    list_display = [
        'name',
        'industry',
        'status_badge',
        'tech_readiness_display',
        'contact_count',
        'phone_display',
        'last_contacted',
        'created_at',
    ]
    list_filter = [
        'status',
        'tech_readiness',
        'industry',
        'region',
        'needs_website',
        'needs_erp',
        'needs_upgrade',
        'needs_custom_system',
        'last_contacted',
        'created_at',
    ]
    search_fields = ['name', 'description', 'address', 'city', 'notes']
    list_editable = []
    readonly_fields = ['created_at', 'updated_at']
    
    # Inlines
    inlines = [ContactPersonInline, PhoneNumberInline, SocialLinkInline, CommunicationLogInline, OpportunityInline]
    
    # Fieldsets for organized form with tab navigation
    fieldsets = (
        (_("Basic Information"), {
            'fields': ('name', 'industry', 'business_type', 'description'),
            'classes': ('tab-basic',)
        }),
        (_("Location"), {
            'fields': ('address', 'city', 'region'),
            'classes': ('tab-location',)
        }),
        (_("Status"), {
            'fields': ('status', 'tech_readiness', 'last_contacted', 'source'),
            'classes': ('tab-status',)
        }),
        (_("Needs"), {
            'fields': ('needs_website', 'needs_erp', 'needs_upgrade', 'needs_custom_system', 'other_needs', 'notes'),
            'classes': ('tab-needs',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom actions
    actions = ['mark_contacted', 'mark_prospect', 'mark_in_discussion', 'mark_client', 'export_as_csv']
    
    @action(description="📥 Export as CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="companies.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Industry', 'Business Type', 'City', 'Region', 
            'Status', 'Tech Readiness', 'Needs Website', 'Needs ERP', 
            'Needs Upgrade', 'Needs Custom System', 'Last Contacted', 'Source', 'Notes'
        ])
        
        for company in queryset:
            writer.writerow([
                company.name,
                company.industry or '',
                company.business_type or '',
                company.city or '',
                company.region or '',
                company.get_status_display(),
                company.tech_readiness or '',
                'Yes' if company.needs_website else 'No',
                'Yes' if company.needs_erp else 'No',
                'Yes' if company.needs_upgrade else 'No',
                'Yes' if company.needs_custom_system else 'No',
                company.last_contacted or '',
                company.source or '',
                company.notes or '',
            ])
        
        return response
    
    @action(description="📞 Mark as Contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f"{updated} companies marked as contacted.", messages.SUCCESS)
    
    @action(description="🔍 Mark as Prospect")
    def mark_prospect(self, request, queryset):
        updated = queryset.update(status='prospect')
        self.message_user(request, f"{updated} companies marked as prospects.", messages.SUCCESS)
    
    @action(description="💬 Mark as In Discussion")
    def mark_in_discussion(self, request, queryset):
        updated = queryset.update(status='in_discussion')
        self.message_user(request, f"{updated} companies marked as in discussion.", messages.SUCCESS)
    
    @action(description="✅ Mark as Client")
    def mark_client(self, request, queryset):
        updated = queryset.update(status='client')
        self.message_user(request, f"{updated} companies marked as clients.", messages.SUCCESS)
    
    @display(description=_("Status"))
    def status_badge(self, obj):
        colors = {
            'prospect': 'bg-gray-100 text-gray-800',
            'contacted': 'bg-blue-100 text-blue-800',
            'in_discussion': 'bg-yellow-100 text-yellow-800',
            'client': 'bg-green-100 text-green-800',
            'closed': 'bg-red-100 text-red-800',
        }
        color = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description=_("Tech Readiness"))
    def tech_readiness_display(self, obj):
        if obj.tech_readiness is None:
            return format_html('<span class="text-gray-400">Not set</span>')
        
        colors = {
            1: 'bg-red-100 text-red-800',
            2: 'bg-orange-100 text-orange-800',
            3: 'bg-yellow-100 text-yellow-800',
            4: 'bg-blue-100 text-blue-800',
            5: 'bg-green-100 text-green-800',
        }
        color = colors.get(obj.tech_readiness, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}/5</span>',
            color,
            obj.tech_readiness
        )
    
    @display(description=_("Contacts"))
    def contact_count(self, obj):
        count = obj.contacts.count()
        return format_html('<span class="font-semibold">{}</span>', count)
    
    @display(description=_("Phone"))
    def phone_display(self, obj):
        phone = obj.primary_phone
        if phone:
            return format_html(
                '<a href="tel:{}" class="text-blue-600 hover:underline">{}</a>',
                phone.number,
                phone.number
            )
        return format_html('<span class="text-gray-400">-</span>')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('contacts', 'phonenumbers', 'sociallinks')


@admin.register(ContactPerson)
class ContactPersonAdmin(ModelAdmin):
    """Admin interface for ContactPerson model."""
    
    list_display = ['name', 'company_link', 'role', 'telegram_handle', 'is_primary_badge', 'phone_count']
    list_filter = ['is_primary', 'company__industry', 'company__status']
    search_fields = ['name', 'role', 'telegram_handle', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [PhoneNumberInline]
    
    fieldsets = (
        (_("Contact Info"), {
            'fields': ('company', 'name', 'role', 'telegram_handle'),
            'classes': ('tab-info',)
        }),
        (_("Settings"), {
            'fields': ('is_primary',),
            'classes': ('tab-details',)
        }),
        (_("Notes"), {
            'fields': ('notes',),
            'classes': ('tab-details',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description=_("Company"))
    def company_link(self, obj):
        return format_html(
            '<a href="/admin/crm/company/{}/" class="text-blue-600 hover:underline">{}</a>',
            obj.company.id,
            obj.company.name
        )
    
    @display(description=_("Primary"))
    def is_primary_badge(self, obj):
        if obj.is_primary:
            return format_html('<span class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Yes</span>')
        return format_html('<span class="text-gray-400">No</span>')
    
    @display(description=_("Phones"))
    def phone_count(self, obj):
        count = obj.phonenumbers.count()
        return format_html('<span class="font-semibold">{}</span>', count)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(ModelAdmin):
    """Admin interface for PhoneNumber model."""
    
    list_display = ['number', 'phone_type_badge', 'company_link', 'contact_link', 'is_primary_badge', 'is_verified_badge']
    list_filter = ['phone_type', 'is_primary', 'is_verified']
    search_fields = ['number', 'company__name', 'contact_person__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_("Phone Info"), {
            'fields': ('number', 'phone_type', 'is_primary', 'is_verified'),
            'classes': ('tab-info',)
        }),
        (_("Owner"), {
            'fields': ('company', 'contact_person'),
            'classes': ('tab-info',)
        }),
        (_("Notes"), {
            'fields': ('notes',),
            'classes': ('tab-info',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description=_("Type"))
    def phone_type_badge(self, obj):
        colors = {
            'mobile': 'bg-blue-100 text-blue-800',
            'landline': 'bg-gray-100 text-gray-800',
            'whatsapp': 'bg-green-100 text-green-800',
            'telegram': 'bg-cyan-100 text-cyan-800',
            'office': 'bg-purple-100 text-purple-800',
            'other': 'bg-gray-100 text-gray-800',
        }
        color = colors.get(obj.phone_type, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_phone_type_display()
        )
    
    @display(description=_("Company"))
    def company_link(self, obj):
        if obj.company:
            return format_html(
                '<a href="/admin/crm/company/{}/" class="text-blue-600 hover:underline">{}</a>',
                obj.company.id,
                obj.company.name
            )
        return format_html('<span class="text-gray-400">-</span>')
    
    @display(description=_("Contact"))
    def contact_link(self, obj):
        if obj.contact_person:
            return format_html(
                '<a href="/admin/crm/contactperson/{}/" class="text-blue-600 hover:underline">{}</a>',
                obj.contact_person.id,
                obj.contact_person.name or 'Unnamed'
            )
        return format_html('<span class="text-gray-400">-</span>')
    
    @display(description=_("Primary"))
    def is_primary_badge(self, obj):
        if obj.is_primary:
            return format_html('<span class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Yes</span>')
        return format_html('<span class="text-gray-400">No</span>')
    
    @display(description=_("Verified"))
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">✓</span>')
        return format_html('<span class="text-gray-400">✗</span>')


@admin.register(SocialLink)
class SocialLinkAdmin(ModelAdmin):
    """Admin interface for SocialLink model."""
    
    list_display = ['platform_badge', 'url_link', 'company_link', 'is_primary_badge']
    list_filter = ['platform', 'is_primary']
    search_fields = ['url', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_("Link Info"), {
            'fields': ('platform', 'url', 'is_primary'),
            'classes': ('tab-info',)
        }),
        (_("Company"), {
            'fields': ('company',),
            'classes': ('tab-info',)
        }),
        (_("Notes"), {
            'fields': ('notes',),
            'classes': ('tab-info',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description=_("Platform"))
    def platform_badge(self, obj):
        colors = {
            'website': 'bg-blue-100 text-blue-800',
            'facebook': 'bg-blue-600 text-white',
            'linkedin': 'bg-blue-700 text-white',
            'twitter': 'bg-sky-500 text-white',
            'instagram': 'bg-pink-500 text-white',
            'telegram': 'bg-cyan-500 text-white',
            '2merkato': 'bg-orange-500 text-white',
            'youtube': 'bg-red-600 text-white',
            'tiktok': 'bg-gray-900 text-white',
            'ethiojobs': 'bg-green-600 text-white',
            'qefira': 'bg-purple-600 text-white',
            'jumia': 'bg-yellow-500 text-white',
            'dealdeal': 'bg-red-500 text-white',
            'other': 'bg-gray-100 text-gray-800',
        }
        color = colors.get(obj.platform, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_platform_display()
        )
    
    @display(description=_("URL"))
    def url_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" class="text-blue-600 hover:underline" rel="noopener noreferrer">🔗 Link</a>',
            obj.url
        )
    
    @display(description=_("Company"))
    def company_link(self, obj):
        return format_html(
            '<a href="/admin/crm/company/{}/" class="text-blue-600 hover:underline">{}</a>',
            obj.company.id,
            obj.company.name
        )
    
    @display(description=_("Primary"))
    def is_primary_badge(self, obj):
        if obj.is_primary:
            return format_html('<span class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Yes</span>')
        return format_html('<span class="text-gray-400">No</span>')


@admin.register(CommunicationLog)
class CommunicationLogAdmin(ModelAdmin):
    """Admin interface for CommunicationLog model."""
    
    list_display = ['date', 'company_link', 'contact_link', 'method_badge', 'outcome_badge', 'next_action_date']
    list_filter = [
        'method',
        'outcome',
        'date',
        'next_action_date',
    ]
    search_fields = ['company__name', 'contact_person__name', 'notes', 'next_action']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_("Communication"), {
            'fields': ('company', 'contact_person', 'date', 'method', 'outcome'),
            'classes': ('tab-comm',)
        }),
        (_("Details"), {
            'fields': ('duration_minutes', 'notes'),
            'classes': ('tab-details',)
        }),
        (_("Next Action"), {
            'fields': ('next_action', 'next_action_date'),
            'classes': ('tab-next',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description=_("Company"))
    def company_link(self, obj):
        return format_html(
            '<a href="/admin/crm/company/{}/" class="text-blue-600 hover:underline">{}</a>',
            obj.company.id,
            obj.company.name
        )
    
    @display(description=_("Contact"))
    def contact_link(self, obj):
        if obj.contact_person:
            return format_html(
                '<a href="/admin/crm/contactperson/{}/" class="text-blue-600 hover:underline">{}</a>',
                obj.contact_person.id,
                obj.contact_person.name or 'Unnamed'
            )
        return format_html('<span class="text-gray-400">-</span>')
    
    @display(description=_("Method"))
    def method_badge(self, obj):
        colors = {
            'phone': 'bg-blue-100 text-blue-800',
            'telegram': 'bg-cyan-100 text-cyan-800',
            'email': 'bg-purple-100 text-purple-800',
            'whatsapp': 'bg-green-100 text-green-800',
            'in_person': 'bg-orange-100 text-orange-800',
            'social_media': 'bg-pink-100 text-pink-800',
            'other': 'bg-gray-100 text-gray-800',
        }
        color = colors.get(obj.method, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_method_display()
        )
    
    @display(description=_("Outcome"))
    def outcome_badge(self, obj):
        if not obj.outcome:
            return format_html('<span class="text-gray-400">-</span>')
        
        colors = {
            'no_answer': 'bg-gray-100 text-gray-800',
            'left_message': 'bg-yellow-100 text-yellow-800',
            'interested': 'bg-green-100 text-green-800',
            'not_interested': 'bg-red-100 text-red-800',
            'follow_up_scheduled': 'bg-blue-100 text-blue-800',
            'meeting_scheduled': 'bg-purple-100 text-purple-800',
            'proposal_sent': 'bg-indigo-100 text-indigo-800',
            'negotiation': 'bg-orange-100 text-orange-800',
            'closed_won': 'bg-green-600 text-white',
            'closed_lost': 'bg-red-600 text-white',
        }
        color = colors.get(obj.outcome, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_outcome_display()
        )


@admin.register(Opportunity)
class OpportunityAdmin(ModelAdmin):
    """Admin interface for Opportunity model."""
    
    list_display = [
        'title',
        'company_link',
        'opportunity_type_badge',
        'status_badge',
        'estimated_value',
        'probability_display',
        'expected_close_date',
    ]
    list_filter = [
        'opportunity_type',
        'status',
        ('estimated_value', RangeNumericFilter),
        ('probability', RangeNumericFilter),
        'expected_close_date',
    ]
    search_fields = ['title', 'company__name', 'description', 'requirements']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'expected_close_date'
    
    fieldsets = (
        (_("Basic Info"), {
            'fields': ('company', 'title', 'opportunity_type', 'status'),
            'classes': ('tab-basic',)
        }),
        (_("Financials"), {
            'fields': ('estimated_value', 'actual_value'),
            'classes': ('tab-financials',)
        }),
        (_("Details"), {
            'fields': ('probability', 'expected_close_date', 'actual_close_date', 'description', 'requirements', 'notes'),
            'classes': ('tab-details',)
        }),
        (_("Loss Analysis"), {
            'fields': ('loss_reason',),
            'classes': ('collapse',)
        }),
        (_("Metadata"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom actions
    actions = ['mark_won', 'mark_lost', 'advance_stage']
    
    @action(description="✅ Mark as Won")
    def mark_won(self, request, queryset):
        updated = queryset.update(status='won')
        self.message_user(request, f"{updated} opportunities marked as won.", messages.SUCCESS)
    
    @action(description="❌ Mark as Lost")
    def mark_lost(self, request, queryset):
        updated = queryset.update(status='lost')
        self.message_user(request, f"{updated} opportunities marked as lost.", messages.SUCCESS)
    
    @action(description="⏭️ Advance Stage")
    def advance_stage(self, request, queryset):
        stage_map = {
            'lead': 'qualified',
            'qualified': 'proposal',
            'proposal': 'negotiation',
            'negotiation': 'won',
        }
        count = 0
        for opp in queryset:
            if opp.status in stage_map:
                opp.status = stage_map[opp.status]
                opp.save()
                count += 1
        self.message_user(request, f"{count} opportunities advanced to next stage.", messages.SUCCESS)
    
    @display(description=_("Company"))
    def company_link(self, obj):
        return format_html(
            '<a href="/admin/crm/company/{}/" class="text-blue-600 hover:underline">{}</a>',
            obj.company.id,
            obj.company.name
        )
    
    @display(description=_("Type"))
    def opportunity_type_badge(self, obj):
        colors = {
            'website': 'bg-blue-100 text-blue-800',
            'erp': 'bg-purple-100 text-purple-800',
            'upgrade': 'bg-orange-100 text-orange-800',
            'custom_system': 'bg-indigo-100 text-indigo-800',
            'mobile_app': 'bg-pink-100 text-pink-800',
            'consulting': 'bg-teal-100 text-teal-800',
            'maintenance': 'bg-gray-100 text-gray-800',
            'other': 'bg-gray-100 text-gray-800',
        }
        color = colors.get(obj.opportunity_type, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_opportunity_type_display()
        )
    
    @display(description=_("Status"))
    def status_badge(self, obj):
        colors = {
            'lead': 'bg-gray-100 text-gray-800',
            'qualified': 'bg-blue-100 text-blue-800',
            'proposal': 'bg-yellow-100 text-yellow-800',
            'negotiation': 'bg-orange-100 text-orange-800',
            'won': 'bg-green-600 text-white',
            'lost': 'bg-red-600 text-white',
            'on_hold': 'bg-gray-200 text-gray-700',
        }
        color = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description=_("Value"))
    def estimated_value(self, obj):
        if obj.estimated_value:
            return format_html('<span class="font-semibold text-green-600">{:,.0f} ETB</span>', obj.estimated_value)
        return format_html('<span class="text-gray-400">-</span>')
    
    @display(description=_("Probability"))
    def probability_display(self, obj):
        if obj.probability is None:
            return format_html('<span class="text-gray-400">-</span>')
        
        if obj.probability >= 70:
            color = 'bg-green-100 text-green-800'
        elif obj.probability >= 40:
            color = 'bg-yellow-100 text-yellow-800'
        else:
            color = 'bg-red-100 text-red-800'
        
        return format_html(
            '<span class="px-2 py-1 rounded-full text-xs font-medium {}">{}%</span>',
            color,
            obj.probability
        )
