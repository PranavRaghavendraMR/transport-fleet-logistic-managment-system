from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from fleet.models import Vehicle, Driver


class Route(models.Model):
    STATUS_SCHEDULED = 'Scheduled'
    STATUS_IN_TRANSIT = 'In Transit'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    route_code = models.CharField(max_length=30, unique=True, verbose_name="Route Code")
    starting_location = models.CharField(max_length=150, verbose_name="Origin / Starting Location")
    destination = models.CharField(max_length=150, verbose_name="Destination")
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Distance (km)")
    estimated_duration_hours = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Est. Duration (Hours)")
    description = models.TextField(blank=True, verbose_name="Route Description & Cargo Details")
    
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.PROTECT, 
        related_name='routes',
        verbose_name="Assigned Vehicle"
    )
    driver = models.ForeignKey(
        Driver, 
        on_delete=models.PROTECT, 
        related_name='routes',
        verbose_name="Assigned Driver"
    )
    
    departure_datetime = models.DateTimeField(verbose_name="Departure Date & Time")
    expected_arrival_datetime = models.DateTimeField(verbose_name="Expected Arrival Date & Time")
    actual_arrival_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Actual Arrival Date & Time")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-departure_datetime']
        verbose_name = "Transportation Route"
        verbose_name_plural = "Transportation Routes"

    def __str__(self):
        return f"{self.route_code}: {self.starting_location} -> {self.destination} ({self.status})"

    def clean(self):
        # 1. Distance & duration checks
        if self.distance_km is not None and self.distance_km <= 0:
            raise ValidationError({'distance_km': "Distance must be greater than zero."})
        
        if self.estimated_duration_hours is not None and self.estimated_duration_hours <= 0:
            raise ValidationError({'estimated_duration_hours': "Estimated duration must be positive."})

        # 2. Timing logic
        if self.departure_datetime and self.expected_arrival_datetime:
            if self.expected_arrival_datetime <= self.departure_datetime:
                raise ValidationError({'expected_arrival_datetime': "Expected arrival must be strictly after departure time."})

        # 3. Vehicle availability validation
        if self.vehicle:
            # Check if vehicle is in maintenance
            if self.vehicle.status == Vehicle.STATUS_MAINTENANCE:
                raise ValidationError({
                    'vehicle': f"Vehicle {self.vehicle.registration_number} is currently under Maintenance and cannot be assigned."
                })
            
            # Check if vehicle is already assigned to another active (Scheduled or In Transit) route overlapping this time
            active_routes = Route.objects.filter(
                vehicle=self.vehicle,
                status__in=[self.STATUS_SCHEDULED, self.STATUS_IN_TRANSIT]
            )
            if self.pk:
                active_routes = active_routes.exclude(pk=self.pk)

            if self.status in [self.STATUS_SCHEDULED, self.STATUS_IN_TRANSIT] and active_routes.exists():
                raise ValidationError({
                    'vehicle': f"Vehicle {self.vehicle.registration_number} is already assigned to active route {active_routes.first().route_code}."
                })

        # 4. Driver eligibility validation
        if self.driver:
            if self.driver.employment_status != Driver.STATUS_ACTIVE:
                raise ValidationError({
                    'driver': f"Driver {self.driver.name} is not currently active (Status: {self.driver.employment_status})."
                })
            if self.driver.is_license_expired:
                raise ValidationError({
                    'driver': f"Driver {self.driver.name}'s licence has expired on {self.driver.license_expiry_date}."
                })
            
            active_driver_routes = Route.objects.filter(
                driver=self.driver,
                status__in=[self.STATUS_SCHEDULED, self.STATUS_IN_TRANSIT]
            )
            if self.pk:
                active_driver_routes = active_driver_routes.exclude(pk=self.pk)

            if self.status in [self.STATUS_SCHEDULED, self.STATUS_IN_TRANSIT] and active_driver_routes.exists():
                raise ValidationError({
                    'driver': f"Driver {self.driver.name} is already assigned to active route {active_driver_routes.first().route_code}."
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # Synchronize vehicle status based on route status
        if self.status == self.STATUS_IN_TRANSIT:
            if self.vehicle.status != Vehicle.STATUS_IN_USE:
                self.vehicle.status = Vehicle.STATUS_IN_USE
                self.vehicle.save(update_fields=['status'])
        elif self.status in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]:
            # Check if vehicle has any other active in-transit routes
            other_active = Route.objects.filter(
                vehicle=self.vehicle, 
                status=self.STATUS_IN_TRANSIT
            ).exclude(pk=self.pk).exists()
            
            if not other_active and self.vehicle.status == Vehicle.STATUS_IN_USE:
                # Set back to available (unless under maintenance)
                has_active_maintenance = self.vehicle.maintenance_records.filter(
                    status__in=['Scheduled', 'In Progress']
                ).exists()
                self.vehicle.status = Vehicle.STATUS_MAINTENANCE if has_active_maintenance else Vehicle.STATUS_AVAILABLE
                self.vehicle.save(update_fields=['status'])

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_SCHEDULED:
            return 'info'
        elif self.status == self.STATUS_IN_TRANSIT:
            return 'primary'
        elif self.status == self.STATUS_COMPLETED:
            return 'success'
        elif self.status == self.STATUS_CANCELLED:
            return 'danger'
        return 'secondary'
