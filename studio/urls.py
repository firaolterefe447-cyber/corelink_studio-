from django.urls import path
from . import views

urlpatterns = [
    path('', views.studio_home, name='studio_home'),
    path('services/', views.services, name='studio_services'),
    path('services/<slug:slug>/', views.service_detail, name='studio_service_detail'),
    path('projects/', views.projects, name='studio_projects'),
    path('projects/<slug:slug>/', views.project_detail, name='studio_project_detail'),
    path('about/', views.about, name='studio_about'),
    path('team/', views.team, name='studio_team'),
    path('contact/', views.contact, name='studio_contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
]
