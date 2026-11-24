from django import forms
from .models import MaintenanceRecord
from fleet.models import Vehicle


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'vehicle', 'maintenance_type', 'description_of_issue', 
            'service_date', 'next_service_date', 'odometer_reading', 
            'technician_name', 'workshop_name', 'spare_parts_cost', 
            'labour_cost', 'status', 'work_completion_notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'description_of_issue': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reported breakdown, faults, or scheduled service task...'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Odometer at workshop entry'}),
            'technician_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chief mechanic / technician'}),
            'workshop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Workshop / Dealership Service Center'}),
            'spare_parts_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_spare_parts_cost'}),
            'labour_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_labour_cost'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'work_completion_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Parts replaced, repairs done, technician sign-off...'}),
        }

    def clean_spare_parts_cost(self):
        cost = self.cleaned_data.get('spare_parts_cost')
        if cost is not None and cost < 0:
            raise forms.ValidationError("Spare parts cost cannot be negative.")
        return cost

    def clean_labour_cost(self):
        cost = self.cleaned_data.get('labour_cost')
        if cost is not None and cost < 0:
            raise forms.ValidationError("Labour cost cannot be negative.")
        return cost
