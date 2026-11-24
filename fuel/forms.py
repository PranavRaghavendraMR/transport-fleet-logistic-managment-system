from django import forms
from .models import FuelRecord


class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = [
            'vehicle', 'fuel_type', 'fuel_quantity', 'fuel_price_per_litre', 
            'fuel_station', 'fuel_date', 'odometer_reading', 
            'invoice_number', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'fuel_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_fuel_qty', 'placeholder': 'e.g. 120.50'}),
            'fuel_price_per_litre': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_fuel_price', 'placeholder': 'e.g. 96.50'}),
            'fuel_station': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Indian Oil Hub - Hosur Road'}),
            'fuel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Current vehicle odometer reading'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fuel receipt or invoice ref #'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Pump attendant, payment mode (Fleet Card/Cash), etc.'}),
        }

    def clean_fuel_quantity(self):
        qty = self.cleaned_data.get('fuel_quantity')
        if qty is not None and qty <= 0:
            raise forms.ValidationError("Fuel quantity must be greater than zero.")
        return qty

    def clean_fuel_price_per_litre(self):
        price = self.cleaned_data.get('fuel_price_per_litre')
        if price is not None and price <= 0:
            raise forms.ValidationError("Fuel price must be greater than zero.")
        return price

    def clean_odometer_reading(self):
        odo = self.cleaned_data.get('odometer_reading')
        if odo is not None and odo < 0:
            raise forms.ValidationError("Odometer reading cannot be negative.")
        return odo
