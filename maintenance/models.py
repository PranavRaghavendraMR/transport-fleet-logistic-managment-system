from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from fleet.models import Vehicle


class MaintenanceRecord(models.Model):
    TYPE_PREVENTIVE = 'Preventive Servicing'
    TYPE_ENGINE = 'Engine Repair'
    TYPE_BRAKE = 'Brake System'
    TYPE_TYRE = 'Tyre Replacement'
    TYPE_ELECTRICAL = 'Electrical System'
    TYPE_BODY = 'Body Work & Paint'
    TYPE_INSPECTION = 'Inspection & Tune-up'
    TYPE_OTHER = 'Other Repair'

    MAINTENANCE_TYPE_CHOICES = [
        (TYPE_PREVENTIVE, 'Preventive Servicing'),
        (TYPE_ENGINE, 'Engine Repair'),
        (TYPE_BRAKE, 'Brake System'),
        (TYPE_TYRE, 'Tyre Replacement'),
        (TYPE_ELECTRICAL, 'Electrical System'),
        (TYPE_BODY, 'Body Work & Paint'),
        (TYPE_INSPECTION, 'Inspection & Tune-up'),
        (TYPE_OTHER, 'Other Repair'),
    ]

    STATUS_SCHEDULED = 'Scheduled'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        related_name='maintenance_records',
        verbose_name="Vehicle"
    )
    maintenance_type = models.CharField(
        max_length=50, 
        choices=MAINTENANCE_TYPE_CHOICES, 
        default=TYPE_PREVENTIVE
    )
    description_of_issue = models.TextField(verbose_name="Description of Issue / Work Requested")
    service_date = models.DateField(verbose_name="Service Date")
    next_service_date = models.DateField(null=True, blank=True, verbose_name="Next Scheduled Service Date")
    odometer_reading = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Odometer at Service (km)")
    technician_name = models.CharField(max_length=120, verbose_name="Assigned Technician")
    workshop_name = models.CharField(max_length=150, verbose_name="Workshop / Service Center Name")
    
    spare_parts_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Spare Parts Cost (₹)"
    )
    labour_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Labour Cost (₹)"
    )
    total_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Total Cost (₹)"
    )
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    work_completion_notes = models.TextField(blank=True, verbose_name="Work Completion Notes & Remarks")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-service_date', '-created_at']
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.maintenance_type} ({self.service_date}) - {self.status}"

    def clean(self):
        if self.spare_parts_cost is not None and self.spare_parts_cost < 0:
            raise ValidationError({'spare_parts_cost': "Spare parts cost cannot be negative."})
        if self.labour_cost is not None and self.labour_cost < 0:
            raise ValidationError({'labour_cost': "Labour cost cannot be negative."})
        if self.odometer_reading is not None and self.odometer_reading < 0:
            raise ValidationError({'odometer_reading': "Odometer reading cannot be negative."})
        if self.service_date and self.next_service_date:
            if self.next_service_date < self.service_date:
                raise ValidationError({'next_service_date': "Next service date cannot precede the current service date."})

    def save(self, *args, **kwargs):
        self.clean()
        # Automatically calculate total maintenance cost
        spare = self.spare_parts_cost or 0
        labour = self.labour_cost or 0
        self.total_cost = spare + labour
        
        super().save(*args, **kwargs)

        # Update vehicle odometer if service odometer is higher
        if self.odometer_reading and self.odometer_reading > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.odometer_reading
            self.vehicle.save(update_fields=['current_odometer'])

        # Automatic vehicle status synchronization:
        if self.status in [self.STATUS_SCHEDULED, self.STATUS_IN_PROGRESS]:
            if self.vehicle.status != Vehicle.STATUS_MAINTENANCE:
                self.vehicle.status = Vehicle.STATUS_MAINTENANCE
                self.vehicle.save(update_fields=['status'])
        elif self.status == self.STATUS_COMPLETED:
            # Check if any other scheduled or in-progress maintenance exists for this vehicle
            active_maintenance = MaintenanceRecord.objects.filter(
                vehicle=self.vehicle,
                status__in=[self.STATUS_SCHEDULED, self.STATUS_IN_PROGRESS]
            ).exclude(pk=self.pk).exists()

            if not active_maintenance:
                # Check if vehicle is on active transit route
                on_route = self.vehicle.routes.filter(status='In Transit').exists()
                self.vehicle.status = Vehicle.STATUS_IN_USE if on_route else Vehicle.STATUS_AVAILABLE
                self.vehicle.save(update_fields=['status'])

    @property
    def is_overdue(self):
        if self.status != self.STATUS_COMPLETED and self.service_date < date.today():
            return True
        return False

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_SCHEDULED:
            return 'info'
        elif self.status == self.STATUS_IN_PROGRESS:
            return 'warning text-dark'
        elif self.status == self.STATUS_COMPLETED:
            return 'success'
        return 'secondary'
