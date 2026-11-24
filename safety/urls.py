from django.urls import path
from . import views

app_name = 'safety'

urlpatterns = [
    path('dashboard/', views.safety_dashboard, name='safety_dashboard'),
    
    # Incidents
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/create/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident_detail'),
    path('incidents/<int:pk>/edit/', views.incident_update, name='incident_update'),
    path('incidents/<int:pk>/delete/', views.incident_delete, name='incident_delete'),
    
    # Inspections
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/create/', views.inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/', views.inspection_detail, name='inspection_detail'),
]
