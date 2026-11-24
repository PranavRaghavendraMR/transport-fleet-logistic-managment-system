from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal
from fleet.models import Vehicle


class FuelRecord(models.Model):
    FUEL_DIESEL = 'Diesel'
    FUEL_PETROL = 'Petrol'
    FUEL_CNG = 'CNG'
    FUEL_ELECTRIC = 'Electric'

    FUEL_TYPE_CHOICES = [
        (FUEL_DIESEL, 'Diesel'),
        (FUEL_PETROL, 'Petrol'),
        (FUEL_CNG, 'CNG'),
        (FUEL_ELECTRIC, 'Electric'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_records')
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default=FUEL_DIESEL)
    fuel_quantity = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Fuel Quantity (Litres / kg / kWh)"
    )
    fuel_price_per_litre = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Price Per Unit (₹)"
    )
    total_fuel_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Total Cost (₹)"
    )
    fuel_station = models.CharField(max_length=150, verbose_name="Fuel Station / Vendor Name")
    fuel_date = models.DateField(verbose_name="Fuel Purchase Date")
    odometer_reading = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Current Odometer (km)")
    
    # Distance and mileage calculations based on consecutive fuel records
    distance_travelled = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Distance Travelled Since Last Refuel (km)"
    )
    calculated_mileage = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.0, 
        verbose_name="Calculated Mileage (km/L)"
    )
    
    recorded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='recorded_fuel_entries',
        verbose_name="Recorded By"
    )
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="Invoice / Bill No.")
    notes = models.TextField(blank=True, verbose_name="Notes & Remarks")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fuel_date', '-odometer_reading', '-created_at']
        verbose_name = "Fuel Record"
        verbose_name_plural = "Fuel Records"

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.fuel_quantity}L @ ₹{self.total_fuel_cost} ({self.fuel_date})"

    def clean(self):
        if self.fuel_quantity is not None and self.fuel_quantity <= 0:
            raise ValidationError({'fuel_quantity': "Fuel quantity must be strictly greater than zero."})
        if self.fuel_price_per_litre is not None and self.fuel_price_per_litre <= 0:
            raise ValidationError({'fuel_price_per_litre': "Fuel price per unit must be greater than zero."})
        if self.odometer_reading is not None and self.odometer_reading < 0:
            raise ValidationError({'odometer_reading': "Odometer reading cannot be negative."})

    def calculate_mileage_from_previous(self):
        """
        Calculates distance travelled and mileage (km/L).
        Assumptions:
        - Uses the immediately preceding fuel record for this vehicle (ordered by fuel_date and odometer_reading).
        - If current odometer > previous odometer and quantity > 0:
          Distance = Current Odometer - Previous Odometer
          Mileage = Distance / Fuel Quantity
        """
        previous_record = FuelRecord.objects.filter(
            vehicle=self.vehicle,
            odometer_reading__lt=self.odometer_reading
        )
        if self.pk:
            previous_record = previous_record.exclude(pk=self.pk)
        
        prev = previous_record.order_by('-odometer_reading', '-fuel_date').first()
        if prev and self.odometer_reading > prev.odometer_reading:
            distance = self.odometer_reading - prev.odometer_reading
            self.distance_travelled = distance
            if self.fuel_quantity and self.fuel_quantity > 0:
                self.calculated_mileage = round(distance / self.fuel_quantity, 2)
        else:
            # First refuel entry for this vehicle or no previous baseline
            self.distance_travelled = Decimal('0.00')
            self.calculated_mileage = Decimal('0.00')

    def save(self, *args, **kwargs):
        self.clean()
        
        # Total cost calculation
        qty = self.fuel_quantity or Decimal('0.00')
        price = self.fuel_price_per_litre or Decimal('0.00')
        self.total_fuel_cost = round(qty * price, 2)
        
        # Calculate mileage
        self.calculate_mileage_from_previous()
        
        super().save(*args, **kwargs)
        
        # Update vehicle current odometer if higher
        if self.odometer_reading and self.odometer_reading > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.odometer_reading
            self.vehicle.save(update_fields=['current_odometer'])
