from django.contrib import admin
from .models import SafetyIncident, SafetyInspection


@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    list_display = (
        'incident_id', 'vehicle', 'driver', 'incident_type', 
        'incident_date', 'damage_severity', 'estimated_damage_cost', 'status'
    )
    list_filter = ('status', 'damage_severity', 'incident_type', 'incident_date')
    search_fields = ('incident_id', 'vehicle__registration_number', 'incident_location', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SafetyInspection)
class SafetyInspectionAdmin(admin.ModelAdmin):
    list_display = (
        'inspection_id', 'vehicle', 'inspection_date', 
        'inspector_name', 'overall_inspection_result'
    )
    list_filter = ('overall_inspection_result', 'inspection_date')
    search_fields = ('inspection_id', 'vehicle__registration_number', 'inspector_name')
    readonly_fields = ('created_at', 'updated_at')
