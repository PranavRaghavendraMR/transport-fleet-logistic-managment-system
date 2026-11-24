from django.db import models
from django.utils import timezone
from datetime import date


class Vehicle(models.Model):
    TYPE_TRUCK = 'Truck'
    TYPE_VAN = 'Van'
    TYPE_BUS = 'Bus'
    TYPE_MINI_TRUCK = 'Mini Truck'
    TYPE_OTHER = 'Other'

    VEHICLE_TYPE_CHOICES = [
        (TYPE_TRUCK, 'Truck'),
        (TYPE_VAN, 'Van'),
        (TYPE_BUS, 'Bus'),
        (TYPE_MINI_TRUCK, 'Mini Truck'),
        (TYPE_OTHER, 'Other'),
    ]

    FUEL_PETROL = 'Petrol'
    FUEL_DIESEL = 'Diesel'
    FUEL_CNG = 'CNG'
    FUEL_ELECTRIC = 'Electric'

    FUEL_TYPE_CHOICES = [
        (FUEL_DIESEL, 'Diesel'),
        (FUEL_PETROL, 'Petrol'),
        (FUEL_CNG, 'CNG'),
        (FUEL_ELECTRIC, 'Electric'),
    ]

    STATUS_AVAILABLE = 'Available'
    STATUS_IN_USE = 'In Use'
    STATUS_MAINTENANCE = 'Maintenance'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_IN_USE, 'In Use'),
        (STATUS_MAINTENANCE, 'Maintenance'),
    ]

    registration_number = models.CharField(max_length=25, unique=True, verbose_name="Registration Number")
    vehicle_type = models.CharField(max_length=25, choices=VEHICLE_TYPE_CHOICES, default=TYPE_TRUCK)
    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    manufacturing_year = models.PositiveIntegerField()
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Capacity (kg)")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default=FUEL_DIESEL)
    current_odometer = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Odometer (km)")
    insurance_expiry_date = models.DateField()
    registration_expiry_date = models.DateField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['registration_number']
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.registration_number} - {self.manufacturer} {self.model_name} ({self.vehicle_type})"

    @property
    def is_insurance_expired(self):
        return self.insurance_expiry_date < date.today()

    @property
    def is_registration_expired(self):
        return self.registration_expiry_date < date.today()

    @property
    def is_insurance_expiring_soon(self):
        delta = (self.insurance_expiry_date - date.today()).days
        return 0 <= delta <= 30

    @property
    def is_registration_expiring_soon(self):
        delta = (self.registration_expiry_date - date.today()).days
        return 0 <= delta <= 30

    @property
    def status_badge_class(self):
        if self.status == self.STATUS_AVAILABLE:
            return 'success'
        elif self.status == self.STATUS_IN_USE:
            return 'primary'
        elif self.status == self.STATUS_MAINTENANCE:
            return 'danger'
        return 'secondary'


class Driver(models.Model):
    STATUS_ACTIVE = 'Active'
    STATUS_ON_LEAVE = 'On Leave'
    STATUS_SUSPENDED = 'Suspended'
    STATUS_TERMINATED = 'Terminated'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ON_LEAVE, 'On Leave'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_TERMINATED, 'Terminated'),
    ]

    name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True, verbose_name="Licence Number")
    license_expiry_date = models.DateField(verbose_name="Licence Expiry Date")
    address = models.TextField()
    employment_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    experience_years = models.PositiveIntegerField(default=1)
    emergency_contact = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

    def __str__(self):
        return f"{self.name} ({self.license_number}) - {self.employment_status}"

    @property
    def is_license_expired(self):
        return self.license_expiry_date < date.today()

    @property
    def is_license_expiring_soon(self):
        delta = (self.license_expiry_date - date.today()).days
        return 0 <= delta <= 30

    @property
    def status_badge_class(self):
        if self.employment_status == self.STATUS_ACTIVE:
            return 'success'
        elif self.employment_status == self.STATUS_ON_LEAVE:
            return 'warning'
        elif self.employment_status == self.STATUS_SUSPENDED:
            return 'danger'
        return 'secondary'
