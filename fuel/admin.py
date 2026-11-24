from django.contrib import admin
from .models import FuelRecord


@admin.register(FuelRecord)
class FuelRecordAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle', 'fuel_date', 'fuel_type', 'fuel_quantity', 
        'fuel_price_per_litre', 'total_fuel_cost', 
        'odometer_reading', 'calculated_mileage', 'fuel_station'
    )
    list_filter = ('fuel_type', 'fuel_date')
    search_fields = ('vehicle__registration_number', 'fuel_station', 'invoice_number')
    readonly_fields = ('total_fuel_cost', 'distance_travelled', 'calculated_mileage', 'created_at', 'updated_at')
