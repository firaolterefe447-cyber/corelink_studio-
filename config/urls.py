from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from studio.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap, TeamMemberSitemap
from django.shortcuts import redirect


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /media/",
        "Allow: /",
        "Sitemap: https://studio.corelink.et/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


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
    path("studio/", include("studio.urls")),  # Studio app under /studio/
]

# Serve static and media files only in DEBUG mode
# In production, Apache (via .htaccess) serves these files directly
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
