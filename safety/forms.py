from django import forms
from .models import SafetyIncident, SafetyInspection


class SafetyIncidentForm(forms.ModelForm):
    class Meta:
        model = SafetyIncident
        fields = [
            'incident_id', 'vehicle', 'driver', 'incident_date', 
            'incident_location', 'incident_type', 'damage_severity', 
            'estimated_damage_cost', 'description', 'action_taken', 'status'
        ]
        widgets = {
            'incident_id': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'e.g. INC-2026-001'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'incident_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'incident_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Highway, City, Landmark, etc.'}),
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'damage_severity': forms.Select(attrs={'class': 'form-select'}),
            'estimated_damage_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed narrative of incident, circumstances, weather, speed...'}),
            'action_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'FIR filed, medical assistance, towing, insurance claim initiated...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_estimated_damage_cost(self):
        cost = self.cleaned_data.get('estimated_damage_cost')
        if cost is not None and cost < 0:
            raise forms.ValidationError("Estimated damage cost cannot be negative.")
        return cost


class SafetyInspectionForm(forms.ModelForm):
    class Meta:
        model = SafetyInspection
        fields = [
            'inspection_id', 'vehicle', 'inspection_date', 'inspector_name', 
            'brake_condition', 'tyre_condition', 'lights_condition', 
            'documents_verification', 'overall_inspection_result', 'remarks'
        ]
        widgets = {
            'inspection_id': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'e.g. INSP-2026-001'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspector_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certified Safety Inspector / Depot Engineer'}),
            'brake_condition': forms.Select(attrs={'class': 'form-select'}),
            'tyre_condition': forms.Select(attrs={'class': 'form-select'}),
            'lights_condition': forms.Select(attrs={'class': 'form-select'}),
            'documents_verification': forms.Select(attrs={'class': 'form-select'}),
            'overall_inspection_result': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brake pad thickness, tread depth, headlight alignment, observations...'}),
        }
