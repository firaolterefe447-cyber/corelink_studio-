from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, Project, TeamMember


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['studio_home', 'studio_about', 'studio_contact', 'studio_services', 'studio_projects']

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Sitemap for service pages"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    """Sitemap for project pages"""
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Project.objects.filter(status='COMPLETED', is_featured=True)

    def lastmod(self, obj):
        return obj.updated_at


class TeamMemberSitemap(Sitemap):
    """Sitemap for team member pages"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return TeamMember.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
