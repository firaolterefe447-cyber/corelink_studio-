from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_dashboard, name='dashboard'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.company_add, name='company_add'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    path('companies/<int:company_id>/activity/', views.activity_timeline, name='activity_timeline'),
    path('contacts/<int:contact_id>/', views.contact_detail, name='contact_detail'),
    path('companies/<int:company_id>/contact/add/', views.contact_add, name='contact_add'),
    path('companies/<int:company_id>/phone/add/', views.phone_add, name='phone_add'),
    path('companies/<int:company_id>/social/add/', views.social_add, name='social_add'),
    path('companies/<int:company_id>/communication/add/', views.communication_add, name='communication_add'),
    path('companies/<int:company_id>/opportunity/add/', views.opportunity_add, name='opportunity_add'),
    path('pipeline/', views.opportunity_pipeline, name='pipeline'),
    path('communications/', views.communication_timeline, name='communications'),
]
