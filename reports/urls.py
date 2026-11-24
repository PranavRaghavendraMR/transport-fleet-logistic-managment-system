from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('vehicles/inventory/', views.vehicle_inventory_report, name='vehicle_inventory_report'),
    path('vehicles/availability/', views.vehicle_availability_report, name='vehicle_availability_report'),
    path('drivers/', views.driver_report, name='driver_report'),
    path('routes/performance/', views.route_performance_report, name='route_performance_report'),
    path('maintenance/history/', views.maintenance_history_report, name='maintenance_history_report'),
    path('maintenance/expenses/', views.maintenance_expense_report, name='maintenance_expense_report'),
    path('safety/incidents/', views.safety_incident_report, name='safety_incident_report'),
    path('fuel/expenses/', views.fuel_expense_report, name='fuel_expense_report'),
    path('fuel/mileage/', views.vehicle_mileage_report, name='vehicle_mileage_report'),
]
