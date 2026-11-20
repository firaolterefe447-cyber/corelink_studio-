from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel

User = get_user_model()


class Company(TimeStampedModel):
    """Core business/company entity - only name is required."""
    
    INDUSTRY_CHOICES = [
        # Technology (keeping old values for backward compatibility)
        ('technology', _('Technology & Software')),
        ('software_dev', _('Software Development')),
        ('it_services', _('IT Services & Support')),
        ('hardware', _('Hardware & Electronics')),
        ('fintech', _('Fintech & Digital Payments')),
        ('telecommunications', _('Telecommunications')),
        ('digital_marketing', _('Digital Marketing & SEO')),
        
        # Banking & Finance (keeping old values for backward compatibility)
        ('banking_finance', _('Banking & Finance')),
        ('banking', _('Banking')),
        ('microfinance', _('Microfinance')),
        ('insurance', _('Insurance')),
        ('investment', _('Investment & Asset Management')),
        ('accounting', _('Accounting & Bookkeeping')),
        
        # Agriculture & Agribusiness (keeping old values for backward compatibility)
        ('agriculture', _('Agriculture & Agribusiness')),
        ('coffee_tea', _('Coffee & Tea Production')),
        ('flower_farming', _('Flower Farming')),
        ('livestock', _('Livestock & Poultry')),
        ('crop_farming', _('Crop Farming')),
        ('agro_processing', _('Agro-Processing')),
        
        # Manufacturing (keeping old values for backward compatibility)
        ('manufacturing', _('Manufacturing')),
        ('textile_garment', _('Textile & Garment')),
        ('textile', _('Textile & Apparel')),
        ('leather', _('Leather & Footwear')),
        ('food_processing', _('Food Processing')),
        ('food_beverage', _('Food & Beverage')),
        ('beverage', _('Beverage Production')),
        ('metal_fabrication', _('Metal Fabrication')),
        ('plastic', _('Plastic Manufacturing')),
        ('construction_materials', _('Construction Materials')),
        ('pharma_manufacturing', _('Pharmaceutical Manufacturing')),
        
        # Retail & E-commerce (keeping old values for backward compatibility)
        ('retail', _('Retail & E-commerce')),
        ('supermarket', _('Supermarket & Grocery')),
        ('fashion_retail', _('Fashion Retail')),
        ('electronics_retail', _('Electronics Retail')),
        ('ecommerce', _('E-commerce')),
        ('wholesale', _('Wholesale & Distribution')),
        
        # Healthcare (keeping old values for backward compatibility)
        ('healthcare', _('Healthcare & Pharmaceuticals')),
        ('hospital', _('Hospital & Medical Center')),
        ('pharmacy', _('Pharmacy')),
        ('clinic', _('Clinic')),
        ('medical_equipment', _('Medical Equipment')),
        ('laboratory', _('Laboratory & Diagnostics')),
        
        # Education (keeping old values for backward compatibility)
        ('education', _('Education & Training')),
        ('university', _('University & College')),
        ('private_school', _('Private School')),
        ('vocational', _('Vocational Training')),
        ('edtech', _('EdTech & E-learning')),
        
        # Construction & Real Estate (keeping old values for backward compatibility)
        ('construction', _('Construction & Real Estate')),
        ('real_estate', _('Real Estate')),
        ('architecture', _('Architecture & Design')),
        ('interior_design', _('Interior Design')),
        
        # Transportation & Logistics (keeping old values for backward compatibility)
        ('transportation', _('Transportation & Logistics')),
        ('logistics', _('Logistics & Freight')),
        ('courier', _('Courier & Delivery')),
        ('import_export', _('Import/Export')),
        ('customs_brokerage', _('Customs Brokerage')),
        
        # Hospitality & Tourism (keeping old values for backward compatibility)
        ('hospitality', _('Hospitality & Tourism')),
        ('hotel', _('Hotel & Lodge')),
        ('restaurant', _('Restaurant & Cafe')),
        ('tour_operator', _('Tour Operator')),
        ('event_management', _('Event Management')),
        
        # Energy & Utilities (keeping old values for backward compatibility)
        ('energy', _('Energy & Utilities')),
        ('renewable_energy', _('Renewable Energy')),
        ('electricity', _('Electricity & Power')),
        ('water', _('Water & Sanitation')),
        
        # Mining & Natural Resources (keeping old values for backward compatibility)
        ('mining', _('Mining & Natural Resources')),
        ('oil_gas', _('Oil & Gas')),
        ('quarry', _('Quarry & Construction Materials')),
        
        # Media & Entertainment (keeping old values for backward compatibility)
        ('media_entertainment', _('Media & Entertainment')),
        ('media', _('Media & Broadcasting')),
        ('advertising', _('Advertising Agency')),
        ('printing', _('Printing & Publishing')),
        ('photography', _('Photography & Studio')),
        
        # Professional Services (keeping old values for backward compatibility)
        ('legal', _('Legal Services')),
        ('consulting', _('Consulting & Professional Services')),
        ('hr_recruitment', _('HR & Recruitment')),
        ('security', _('Security Services')),
        ('cleaning', _('Cleaning Services')),
        
        # Government & NGO (keeping old values for backward compatibility)
        ('government', _('Government & Public Sector')),
        ('ngo', _('NGO & Non-Profit')),
        ('international_org', _('International Organization')),
        
        # Other
        ('other', _('Other')),
    ]
    
    # Basic Information
    name = models.CharField(
        max_length=255,
        help_text=_("Company or business name")
    )
    
    # Optional Details
    industry = models.CharField(
        max_length=50,
        choices=INDUSTRY_CHOICES,
        blank=True,
        null=True,
        help_text=_("Industry sector")
    )
    business_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Type of business (e.g., LLC, PLC, Sole Proprietorship)")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("What the company does, current tech stack, etc.")
    )
    
    # Location
    address = models.TextField(
        blank=True,
        null=True,
        help_text=_("Full physical address")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("City")
    )
    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Region/State")
    )
    
    # Status & Tracking
    STATUS_CHOICES = [
        ('prospect', _('Prospect')),
        ('contacted', _('Contacted')),
        ('in_discussion', _('In Discussion')),
        ('client', _('Client')),
        ('closed', _('Closed')),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='prospect',
        help_text=_("Current status in pipeline")
    )
    
    TECH_READINESS_CHOICES = [
        (1, _('Very Low - No tech presence')),
        (2, _('Low - Basic website only')),
        (3, _('Medium - Some digital presence')),
        (4, _('High - Good tech stack')),
        (5, _('Very High - Advanced tech infrastructure')),
    ]
    tech_readiness = models.IntegerField(
        choices=TECH_READINESS_CHOICES,
        blank=True,
        null=True,
        help_text=_("Assessment of current technology level (1-5)")
    )
    
    # Needs Assessment
    needs_website = models.BooleanField(
        default=False,
        help_text=_("Needs website development")
    )
    needs_erp = models.BooleanField(
        default=False,
        help_text=_("Needs ERP system")
    )
    needs_upgrade = models.BooleanField(
        default=False,
        help_text=_("Needs system upgrade")
    )
    needs_custom_system = models.BooleanField(
        default=False,
        help_text=_("Needs custom software solution")
    )
    other_needs = models.TextField(
        blank=True,
        null=True,
        help_text=_("Other specific needs")
    )
    
    # Tracking
    last_contacted = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date of last contact")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("General notes about the company")
    )
    
    # Metadata
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Where did we find this company?")
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = _("Companies")
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['tech_readiness']),
            models.Index(fields=['industry']),
            models.Index(fields=['region']),
            models.Index(fields=['last_contacted']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def primary_phone(self):
        """Get primary phone number if exists."""
        return self.phonenumbers.filter(is_primary=True).first()
    
    @property
    def primary_link(self):
        """Get primary link if exists."""
        return self.sociallinks.filter(is_primary=True).first()
    
    @property
    def total_opportunities_value(self):
        """Sum of all opportunity values."""
        return self.opportunities.aggregate(
            total=models.Sum('estimated_value')
        )['total'] or 0


class ContactPerson(TimeStampedModel):
    """Individual contact person at a company."""
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text=_("Company this person belongs to")
    )
    
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Contact person name")
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Job title/role")
    )
    telegram_handle = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Telegram username (without @)")
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Direct phone number for this contact")
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("Is this the primary contact?")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("Notes about this contact")
    )
    
    class Meta:
        ordering = ['-is_primary', 'name']
        verbose_name_plural = _("Contact People")
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}" if self.name else f"Contact - {self.company.name}"


class PhoneNumber(TimeStampedModel):
    """Unlimited phone numbers for companies or contacts."""
    
    PHONE_TYPE_CHOICES = [
        ('mobile', _('Mobile')),
        ('landline', _('Landline')),
        ('whatsapp', _('WhatsApp')),
        ('telegram', _('Telegram')),
        ('office', _('Office')),
        ('other', _('Other')),
    ]
    
    # Can belong to company or contact person
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='phonenumbers',
        blank=True,
        null=True,
        help_text=_("Company this number belongs to")
    )
    contact_person = models.ForeignKey(
        ContactPerson,
        on_delete=models.CASCADE,
        related_name='phonenumbers',
        blank=True,
        null=True,
        help_text=_("Contact person this number belongs to")
    )
    
    number = models.CharField(
        max_length=20,
        help_text=_("Phone number")
    )
    phone_type = models.CharField(
        max_length=20,
        choices=PHONE_TYPE_CHOICES,
        default='mobile',
        help_text=_("Type of phone number")
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("Is this the primary number?")
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Has this number been verified?")
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Notes about this number")
    )
    
    class Meta:
        ordering = ['-is_primary', 'number']
        verbose_name_plural = _("Phone Numbers")
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['contact_person']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return self.number


class SocialLink(TimeStampedModel):
    """Unlimited social media and profile links for companies."""
    
    PLATFORM_CHOICES = [
        ('website', _('Website')),
        ('facebook', _('Facebook (facebook.com)')),
        ('linkedin', _('LinkedIn (linkedin.com)')),
        ('twitter', _('Twitter/X (x.com)')),
        ('instagram', _('Instagram (instagram.com)')),
        ('telegram', _('Telegram (t.me)')),
        ('2merkato', _('2Merkato (2merkato.com)')),
        ('youtube', _('YouTube (youtube.com)')),
        ('tiktok', _('TikTok (tiktok.com)')),
        ('ethiojobs', _('EthioJobs (ethiojobs.net)')),
        ('qefira', _('Qefira (qefira.com)')),
        ('jumia', _('Jumia (jumia.com)')),
        ('dealdeal', _('DealDeal (dealdeal.et)')),
        ('hulunem', _('Hulunem (hulunem.com)')),
        ('aksion', _('Aksion (aksion.et)')),
        ('addisbiz', _('AddisBiz (addisbiz.com)')),
        ('shegergebeta', _('ShegerGeBeta (shegergebeta.com)')),
        ('mindtrip', _('MindTrip (mindtrip.ai)')),
        ('amrogn', _('Amrogn (amrogn.com)')),
        ('ethioclinics', _('EthioClinics (ethioclinics.com)')),
        ('bina', _('Bina (bina.et)')),
        ('businesses', _('Businesses.et (businesses.et)')),
        ('ethiobusinesses', _('EthioBusinesses (ethiobusinesses.com)')),
        ('moderntenders', _('ModernTenders (moderntenders.com)')),
        ('other', _('Other')),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='sociallinks',
        help_text=_("Company this link belongs to")
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text=_("Platform name")
    )
    url = models.URLField(
        help_text=_("Full URL to the profile/page")
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("Is this the primary link?")
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Notes about this link")
    )
    
    class Meta:
        ordering = ['-is_primary', 'platform']
        verbose_name_plural = _("Social Links")
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['platform']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f"{self.get_platform_display()} - {self.company.name}"


class CommunicationLog(TimeStampedModel):
    """Track all communications with companies."""
    
    METHOD_CHOICES = [
        ('phone', _('Phone Call')),
        ('telegram', _('Telegram')),
        ('email', _('Email')),
        ('whatsapp', _('WhatsApp')),
        ('in_person', _('In Person')),
        ('social_media', _('Social Media')),
        ('other', _('Other')),
    ]
    
    OUTCOME_CHOICES = [
        ('no_answer', _('No Answer')),
        ('left_message', _('Left Message')),
        ('interested', _('Interested')),
        ('not_interested', _('Not Interested')),
        ('follow_up_scheduled', _('Follow-up Scheduled')),
        ('meeting_scheduled', _('Meeting Scheduled')),
        ('proposal_sent', _('Proposal Sent')),
        ('negotiation', _('In Negotiation')),
        ('closed_won', _('Closed Won')),
        ('closed_lost', _('Closed Lost')),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='communications',
        help_text=_("Company this communication is with")
    )
    contact_person = models.ForeignKey(
        ContactPerson,
        on_delete=models.SET_NULL,
        related_name='communications',
        blank=True,
        null=True,
        help_text=_("Contact person spoken with")
    )
    
    date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date of communication")
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        help_text=_("Communication method")
    )
    outcome = models.CharField(
        max_length=30,
        choices=OUTCOME_CHOICES,
        blank=True,
        null=True,
        help_text=_("Outcome of communication")
    )
    duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_("Duration in minutes")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("Detailed notes about the conversation")
    )
    next_action = models.TextField(
        blank=True,
        null=True,
        help_text=_("Next action to take")
    )
    next_action_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date for next action")
    )
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = _("Communication Logs")
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['date']),
            models.Index(fields=['method']),
            models.Index(fields=['outcome']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.get_method_display()} - {self.date.strftime('%Y-%m-%d')}"


class Opportunity(TimeStampedModel):
    """Track sales opportunities and projects."""
    
    TYPE_CHOICES = [
        ('website', _('Website Development')),
        ('erp', _('ERP System')),
        ('upgrade', _('System Upgrade')),
        ('custom_system', _('Custom Software')),
        ('mobile_app', _('Mobile App')),
        ('consulting', _('Consulting')),
        ('maintenance', _('Maintenance')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('lead', _('Lead')),
        ('qualified', _('Qualified')),
        ('proposal', _('Proposal Sent')),
        ('negotiation', _('Negotiation')),
        ('won', _('Won')),
        ('lost', _('Lost')),
        ('on_hold', _('On Hold')),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='opportunities',
        help_text=_("Company this opportunity is with")
    )
    
    title = models.CharField(
        max_length=255,
        help_text=_("Opportunity/project title")
    )
    opportunity_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text=_("Type of opportunity")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='lead',
        help_text=_("Current status")
    )
    
    # Financials
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Estimated value in ETB")
    )
    actual_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Actual value if won")
    )
    
    # Probability & Timeline
    probability = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Win probability percentage (0-100)")
    )
    expected_close_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Expected closing date")
    )
    actual_close_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Actual closing date")
    )
    
    # Details
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Detailed description of the opportunity")
    )
    requirements = models.TextField(
        blank=True,
        null=True,
        help_text=_("Client requirements")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text=_("Additional notes")
    )
    
    # Loss reason if lost
    loss_reason = models.TextField(
        blank=True,
        null=True,
        help_text=_("Reason if opportunity was lost")
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = _("Opportunities")
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['status']),
            models.Index(fields=['opportunity_type']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"


class ActivityLog(TimeStampedModel):
    """Track all user activities in the CRM for audit trail and team visibility."""

    ACTION_CHOICES = [
        ('company_created', _('Company Created')),
        ('company_updated', _('Company Updated')),
        ('contact_created', _('Contact Created')),
        ('contact_updated', _('Contact Updated')),
        ('phone_created', _('Phone Number Added')),
        ('phone_updated', _('Phone Number Updated')),
        ('social_created', _('Social Link Added')),
        ('social_updated', _('Social Link Updated')),
        ('communication_logged', _('Communication Logged')),
        ('opportunity_created', _('Opportunity Created')),
        ('opportunity_updated', _('Opportunity Updated')),
        ('opportunity_won', _('Opportunity Won')),
        ('opportunity_lost', _('Opportunity Lost')),
        ('status_changed', _('Status Changed')),
        ('note_added', _('Note Added')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='crm_activities',
        help_text=_("User who performed the action")
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        help_text=_("Type of action performed")
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text=_("Company this activity relates to")
    )

    description = models.TextField(
        help_text=_("Detailed description of the activity")
    )

    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Additional metadata about the activity")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = _("Activity Logs")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['company']),
            models.Index(fields=['action']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.company.name} by {self.user}"
