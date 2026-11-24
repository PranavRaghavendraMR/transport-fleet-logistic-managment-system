from django.contrib import admin
from .models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        'route_code', 'starting_location', 'destination', 
        'distance_km', 'vehicle', 'driver', 
        'departure_datetime', 'status'
    )
    list_filter = ('status', 'departure_datetime')
    search_fields = ('route_code', 'starting_location', 'destination', 'vehicle__registration_number', 'driver__name')
    readonly_fields = ('created_at', 'updated_at')
