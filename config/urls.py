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
    """Custom media file serving view that bypasses web server configuration"""
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(full_path):
        raise Http404("Media file not found")
    return FileResponse(open(full_path, 'rb'))


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
    path("", include("studio.urls")),  # Studio app at root
    path("studio/", include("studio.urls")),  # Studio app under /studio/ (for backward compatibility)
]

# Serve static files via Whitenoise
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files via custom Django view (bypasses web server configuration)
if not settings.DEBUG:
    urlpatterns += [path('media/<path:path>', serve_media, name='serve_media')]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
