from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_dashboard, name='dashboard'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    path('pipeline/', views.opportunity_pipeline, name='pipeline'),
    path('communications/', views.communication_timeline, name='communications'),
]
