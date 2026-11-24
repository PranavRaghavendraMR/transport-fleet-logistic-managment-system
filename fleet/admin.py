from django.contrib import admin
from .models import Vehicle, Driver


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'registration_number', 'manufacturer', 'model_name', 
        'vehicle_type', 'fuel_type', 'capacity_kg', 
        'current_odometer', 'status', 'insurance_expiry_date'
    )
    list_filter = ('status', 'vehicle_type', 'fuel_type', 'manufacturer')
    search_fields = ('registration_number', 'manufacturer', 'model_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'license_number', 'contact_number', 
        'employment_status', 'license_expiry_date', 'experience_years'
    )
    list_filter = ('employment_status',)
    search_fields = ('name', 'license_number', 'contact_number')
    readonly_fields = ('created_at', 'updated_at')
