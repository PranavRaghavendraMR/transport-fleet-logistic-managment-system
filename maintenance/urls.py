from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('dashboard/', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('', views.maintenance_list, name='maintenance_list'),
    path('create/', views.maintenance_create, name='maintenance_create'),
    path('<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
    path('<int:pk>/edit/', views.maintenance_update, name='maintenance_update'),
    path('<int:pk>/quick-status/', views.maintenance_quick_status, name='maintenance_quick_status'),
    path('<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
]
