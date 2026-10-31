from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.http import HttpResponse, FileResponse, Http404
from django.contrib.sitemaps.views import sitemap
from studio.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap, TeamMemberSitemap
from django.shortcuts import redirect
import os


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /media/",
        "Allow: /",
        "Sitemap: https://studio.corelink.et/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def serve_media(request, path):
    """Serve media files through Django to bypass LiteSpeed's inconsistent behavior"""
    path = path.lstrip('/')
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if not os.path.abspath(full_path).startswith(os.path.abspath(settings.MEDIA_ROOT)):
        raise Http404("Invalid path")
    
    if not os.path.exists(full_path):
        raise Http404(f"Media file not found: {path}")
    
    try:
        file_handle = open(full_path, 'rb')
        return FileResponse(file_handle)
    except IOError:
        raise Http404("Could not read file")


sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'projects': ProjectSitemap,
    'team': TeamMemberSitemap,
}

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.png")),
    ),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("admin/", admin.site.urls),
    path("crm/", include("crm.urls")),  # CRM system
    path("", include("studio.urls")),  # Studio app at root
    path("studio/", include("studio.urls")),  # Studio app under /studio/ (for backward compatibility)
]

# Serve static files via Whitenoise
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files via Django in production (bypasses LiteSpeed inconsistency)
# In DEBUG, use Django's standard static helper
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [path('media/<path:path>', serve_media, name='serve_media')]
