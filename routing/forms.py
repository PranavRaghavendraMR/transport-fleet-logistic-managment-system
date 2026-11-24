from django import forms
from .models import Route
from fleet.models import Vehicle, Driver


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            'route_code', 'starting_location', 'destination', 
            'distance_km', 'estimated_duration_hours', 'description', 
            'vehicle', 'driver', 'departure_datetime', 
            'expected_arrival_datetime', 'actual_arrival_datetime', 'status'
        ]
        widgets = {
            'route_code': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'e.g. RT-BLR-CHE-01'}),
            'starting_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Origin city / hub (e.g. Bengaluru Hub)'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination (e.g. Chennai Port)'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '345.5'}),
            'estimated_duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '7.5'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Cargo type, customer notes, consignment code...'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'departure_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expected_arrival_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'actual_arrival_datetime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter available vehicles: show Available vehicles or current vehicle if editing
        if not self.instance.pk:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(status=Vehicle.STATUS_AVAILABLE)
            self.fields['driver'].queryset = Driver.objects.filter(employment_status=Driver.STATUS_ACTIVE)
        else:
            # When editing, permit the currently assigned vehicle/driver
            v_ids = list(Vehicle.objects.filter(status=Vehicle.STATUS_AVAILABLE).values_list('id', flat=True))
            if self.instance.vehicle_id:
                v_ids.append(self.instance.vehicle_id)
            self.fields['vehicle'].queryset = Vehicle.objects.filter(id__in=v_ids)
            
            d_ids = list(Driver.objects.filter(employment_status=Driver.STATUS_ACTIVE).values_list('id', flat=True))
            if self.instance.driver_id:
                d_ids.append(self.instance.driver_id)
            self.fields['driver'].queryset = Driver.objects.filter(id__in=d_ids)
