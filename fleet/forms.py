from django import forms
from .models import Vehicle, Driver


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'registration_number', 'vehicle_type', 'manufacturer', 
            'model_name', 'manufacturing_year', 'capacity_kg', 
            'fuel_type', 'current_odometer', 'insurance_expiry_date', 
            'registration_expiry_date', 'status', 'notes'
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'e.g. KA-01-AB-1234'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tata Motors'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Prima 4440.S'}),
            'manufacturing_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2030}),
            'capacity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 15000'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'current_odometer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 45200.5'}),
            'insurance_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional specifications or remarks...'}),
        }

    def clean_capacity_kg(self):
        cap = self.cleaned_data.get('capacity_kg')
        if cap is not None and cap <= 0:
            raise forms.ValidationError("Capacity must be greater than zero.")
        return cap

    def clean_current_odometer(self):
        odo = self.cleaned_data.get('current_odometer')
        if odo is not None and odo < 0:
            raise forms.ValidationError("Odometer reading cannot be negative.")
        return odo

    def clean_registration_number(self):
        reg = self.cleaned_data.get('registration_number')
        if reg:
            reg = reg.strip().upper()
            existing = Vehicle.objects.filter(registration_number__iexact=reg)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f"Vehicle with registration number {reg} already exists.")
        return reg


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            'name', 'contact_number', 'license_number', 
            'license_expiry_date', 'address', 'employment_status', 
            'experience_years', 'emergency_contact'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'e.g. KA0120190012345'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential address'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency phone number'}),
        }

    def clean_license_number(self):
        lic = self.cleaned_data.get('license_number')
        if lic:
            lic = lic.strip().upper()
            existing = Driver.objects.filter(license_number__iexact=lic)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f"Driver with licence number {lic} already exists.")
        return lic
