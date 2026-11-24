from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from fleet.models import Vehicle, Driver


class SafetyIncident(models.Model):
    SEVERITY_LOW = 'Low'
    SEVERITY_MEDIUM = 'Medium'
    SEVERITY_HIGH = 'High'
    SEVERITY_CRITICAL = 'Critical'

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, 'Low - Minor Cosmetic / No Injury'),
        (SEVERITY_MEDIUM, 'Medium - Moderate Vehicle Damage'),
        (SEVERITY_HIGH, 'High - Major Mechanical/Body Damage'),
        (SEVERITY_CRITICAL, 'Critical - Severe Accident / Structural Damage'),
    ]

    STATUS_REPORTED = 'Reported'
    STATUS_INVESTIGATING = 'Under Investigation'
    STATUS_RESOLVED = 'Resolved'
    STATUS_CLOSED = 'Closed'

    STATUS_CHOICES = [
        (STATUS_REPORTED, 'Reported'),
        (STATUS_INVESTIGATING, 'Under Investigation'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    TYPE_COLLISION = 'Collision'
    TYPE_MINOR_SCRAPE = 'Minor Scrape / Dent'
    TYPE_BREAKDOWN = 'Mechanical Breakdown'
    TYPE_OVERSPEEDING = 'Overspeeding / Traffic Violation'
    TYPE_CARGO_DAMAGE = 'Cargo Damage'
    TYPE_NEAR_MISS = 'Near Miss Hazard'
    TYPE_OTHER = 'Other Incident'

    INCIDENT_TYPE_CHOICES = [
        (TYPE_COLLISION, 'Collision'),
        (TYPE_MINOR_SCRAPE, 'Minor Scrape / Dent'),
        (TYPE_BREAKDOWN, 'Mechanical Breakdown'),
        (TYPE_OVERSPEEDING, 'Overspeeding / Traffic Violation'),
        (TYPE_CARGO_DAMAGE, 'Cargo Damage'),
        (TYPE_NEAR_MISS, 'Near Miss Hazard'),
        (TYPE_OTHER, 'Other Incident'),
    ]

    incident_id = models.CharField(max_length=30, unique=True, verbose_name="Incident ID")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='incidents')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    incident_date = models.DateField(verbose_name="Incident Date")
    incident_location = models.CharField(max_length=200, verbose_name="Incident Location")
    incident_type = models.CharField(max_length=60, choices=INCIDENT_TYPE_CHOICES, default=TYPE_MINOR_SCRAPE)
    description = models.TextField(verbose_name="Detailed Description of Incident")
    damage_severity = models.CharField(max_length=25, choices=SEVERITY_CHOICES, default=SEVERITY_LOW)
    estimated_damage_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Estimated Damage Cost (₹)"
    )
    action_taken = models.TextField(verbose_name="Action Taken & Preventive Measures")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_REPORTED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-incident_date', '-created_at']
        verbose_name = "Safety Incident"
        verbose_name_plural = "Safety Incidents"

    def __str__(self):
        return f"{self.incident_id}: {self.vehicle.registration_number} - {self.incident_type} ({self.damage_severity})"

    def clean(self):
        if self.estimated_damage_cost is not None and self.estimated_damage_cost < 0:
            raise ValidationError({'estimated_damage_cost': "Estimated damage cost cannot be negative."})

    @property
    def severity_badge_class(self):
        if self.damage_severity == self.SEVERITY_LOW:
            return 'info'
        elif self.damage_severity == self.SEVERITY_MEDIUM:
            return 'warning text-dark'
        elif self.damage_severity == self.SEVERITY_HIGH:
            return 'orange'
        elif self.damage_severity == self.SEVERITY_CRITICAL:
            return 'danger'
        return 'secondary'

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_REPORTED:
            return 'danger'
        elif self.status == self.STATUS_INVESTIGATING:
            return 'warning text-dark'
        elif self.status == self.STATUS_RESOLVED:
            return 'success'
        elif self.status == self.STATUS_CLOSED:
            return 'secondary'
        return 'primary'


class SafetyInspection(models.Model):
    RESULT_PASSED = 'Passed'
    RESULT_CONDITIONAL = 'Conditional Pass'
    RESULT_FAILED = 'Failed'

    RESULT_CHOICES = [
        (RESULT_PASSED, 'Passed - Roadworthy'),
        (RESULT_CONDITIONAL, 'Conditional Pass - Minor Corrections Required'),
        (RESULT_FAILED, 'Failed - Unsafe for Road Operation'),
    ]

    CONDITION_PASS = 'Pass'
    CONDITION_ATTENTION = 'Attention Needed'
    CONDITION_FAIL = 'Fail'

    CONDITION_CHOICES = [
        (CONDITION_PASS, 'Pass / Good'),
        (CONDITION_ATTENTION, 'Attention Needed / Marginal'),
        (CONDITION_FAIL, 'Fail / Defective'),
    ]

    DOC_VALID = 'Valid'
    DOC_ATTENTION = 'Expiring Soon'
    DOC_EXPIRED = 'Expired / Incomplete'

    DOC_CHOICES = [
        (DOC_VALID, 'Valid & Verified'),
        (DOC_ATTENTION, 'Expiring Within 30 Days'),
        (DOC_EXPIRED, 'Expired / Missing Documents'),
    ]

    inspection_id = models.CharField(max_length=30, unique=True, verbose_name="Inspection ID")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections')
    inspection_date = models.DateField(verbose_name="Inspection Date")
    inspector_name = models.CharField(max_length=120, verbose_name="Inspector / Officer Name")
    brake_condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default=CONDITION_PASS)
    tyre_condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default=CONDITION_PASS)
    lights_condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default=CONDITION_PASS)
    documents_verification = models.CharField(max_length=30, choices=DOC_CHOICES, default=DOC_VALID)
    overall_inspection_result = models.CharField(max_length=30, choices=RESULT_CHOICES, default=RESULT_PASSED)
    remarks = models.TextField(blank=True, verbose_name="Inspection Findings & Remarks")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-inspection_date', '-created_at']
        verbose_name = "Safety Inspection"
        verbose_name_plural = "Safety Inspections"

    def __str__(self):
        return f"{self.inspection_id}: {self.vehicle.registration_number} - {self.overall_inspection_result} ({self.inspection_date})"

    @property
    def result_badge_class(self):
        if self.overall_inspection_result == self.RESULT_PASSED:
            return 'success'
        elif self.overall_inspection_result == self.RESULT_CONDITIONAL:
            return 'warning text-dark'
        elif self.overall_inspection_result == self.RESULT_FAILED:
            return 'danger'
        return 'secondary'
