from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Service(models.Model):
    """Services offered by CoreLink Studio"""
    SERVICE_CHOICES = [
        ('WEB', 'Web Development'),
        ('MOBILE', 'Mobile Applications'),
        ('AI', 'AI & Machine Learning'),
        ('ERP', 'Enterprise Resource Planning'),
        ('CLOUD', 'Cloud Solutions'),
        ('CONSULTING', 'IT Consulting'),
        ('DESIGN', 'UI/UX Design'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='WEB')
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Lucide icon name (e.g., 'code', 'smartphone')")
    features = models.JSONField(default=list, help_text="List of service features")
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_icon_url(self):
        return f"/static/img/icons/{self.icon}.svg"


class Project(models.Model):
    """Portfolio projects showcase"""
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMING_SOON', 'Coming Soon'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    technologies = models.JSONField(default=list, help_text="List of technologies used")
    project_url = models.URLField(blank=True, help_text="Live project URL")
    github_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='studio/projects/thumbnails/', blank=True)
    cover_image = models.ImageField(upload_to='studio/projects/covers/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    is_featured = models.BooleanField(default=False)
    completion_date = models.DateField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else ''

    def get_cover_url(self):
        return self.cover_image.url if self.cover_image else ''


class Testimonial(models.Model):
    """Client testimonials"""
    client_name = models.CharField(max_length=200)
    client_company = models.CharField(max_length=200, blank=True)
    client_position = models.CharField(max_length=200, blank=True)
    client_avatar = models.ImageField(upload_to='studio/testimonials/avatars/', blank=True)
    testimonial_text = models.TextField()
    rating = models.IntegerField(default=5, help_text="Rating out of 5")
    project_link = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.client_company}"

    def get_avatar_url(self):
        return self.client_avatar.url if self.client_avatar else ''


class TeamMember(models.Model):
    """Team members showcase"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200, blank=True, help_text="Job title or position")
    photo = models.ImageField(upload_to='studio/team/photos/', blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.title}"

    def get_photo_url(self):
        return self.photo.url if self.photo else ''


class StudioPage(models.Model):
    """CMS for studio page content"""
    PAGE_CHOICES = [
        ('HOME', 'Home Page'),
        ('ABOUT', 'About Page'),
        ('CONTACT', 'Contact Page'),
    ]
    
    page_type = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    hero_title = models.CharField(max_length=300)
    hero_subtitle = models.TextField()
    hero_cta_text = models.CharField(max_length=100, default="Get Started")
    hero_cta_link = models.CharField(max_length=200, default="/contact")
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_page_type_display()} Content"


def validate_hero_image(f):
    if f.size > 5 * 1024 * 1024:
        raise ValidationError("Image must be under 5 MB. Export as WebP or JPG, about 576 px wide.")


class HeroSlide(models.Model):
    """App screenshots shown inside the phone in the home page hero (max 6 active)."""
    MAX_ACTIVE = 6

    title = models.CharField(max_length=200, help_text="Internal name, e.g. 'Discover' or 'Marketplace'")
    image = models.ImageField(
        upload_to='studio/hero/',
        validators=[validate_hero_image],
        help_text="Portrait app screenshot, status bar already cropped off (about 576 x 1220 px). WebP/JPG/PNG under 5 MB.",
    )
    alt_text = models.CharField(max_length=200, blank=True, help_text="Describe the screen for accessibility")
    label = models.CharField(max_length=60, blank=True, help_text="Short caption shown beside the phone, e.g. 'Verified talent'")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Hero slide'
        verbose_name_plural = 'Hero slides'

    def clean(self):
        if self.is_active:
            others = HeroSlide.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if others >= self.MAX_ACTIVE:
                raise ValidationError(f"Only {self.MAX_ACTIVE} slides can be active at once. Deactivate another first.")

    def __str__(self):
        return f"{self.order}. {self.title}"

    def get_image_url(self):
        return self.image.url if self.image else ''
