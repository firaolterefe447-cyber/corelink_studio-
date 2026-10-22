from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from studio.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap, TeamMemberSitemap


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
    path("", include("studio.urls")),  # Studio app at root
]

# Serve media files in both DEBUG and production for cPanel
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Always serve media files (production web server should handle this ideally, but this ensures it works on cPanel)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
