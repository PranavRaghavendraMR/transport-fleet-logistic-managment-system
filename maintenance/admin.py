from django.contrib import admin
from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle', 'maintenance_type', 'service_date', 
        'workshop_name', 'technician_name', 'total_cost', 'status'
    )
    list_filter = ('status', 'maintenance_type', 'service_date')
    search_fields = ('vehicle__registration_number', 'workshop_name', 'technician_name', 'description_of_issue')
    readonly_fields = ('total_cost', 'created_at', 'updated_at')
