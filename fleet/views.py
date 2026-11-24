from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehicle, Driver
from .forms import VehicleForm, DriverForm
from accounts.decorators import fleet_manager_required, admin_required


# Vehicle Views
@login_required
def vehicle_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    fuel_filter = request.GET.get('fuel', '')

    vehicles = Vehicle.objects.all()

    if search_query:
        vehicles = vehicles.filter(
            Q(registration_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(model_name__icontains=search_query)
        )
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if type_filter:
        vehicles = vehicles.filter(vehicle_type=type_filter)
    if fuel_filter:
        vehicles = vehicles.filter(fuel_type=fuel_filter)

    context = {
        'vehicles': vehicles,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'fuel_filter': fuel_filter,
        'vehicle_types': Vehicle.VEHICLE_TYPE_CHOICES,
        'statuses': Vehicle.STATUS_CHOICES,
        'fuel_types': Vehicle.FUEL_TYPE_CHOICES,
    }
    return render(request, 'fleet/vehicle_list.html', context)


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    recent_routes = vehicle.routes.select_related('driver').order_by('-departure_datetime')[:5]
    maintenance_history = vehicle.maintenance_records.order_by('-service_date')[:5]
    fuel_history = vehicle.fuel_records.order_by('-fuel_date')[:5]
    safety_incidents = vehicle.incidents.select_related('driver').order_by('-incident_date')[:5]
    inspections = vehicle.inspections.order_by('-inspection_date')[:5]

    context = {
        'vehicle': vehicle,
        'recent_routes': recent_routes,
        'maintenance_history': maintenance_history,
        'fuel_history': fuel_history,
        'safety_incidents': safety_incidents,
        'inspections': inspections,
    }
    return render(request, 'fleet/vehicle_detail.html', context)


@login_required
@fleet_manager_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.registration_number} has been registered successfully.")
            return redirect('fleet:vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm()
    return render(request, 'fleet/vehicle_form.html', {'form': form, 'title': 'Register New Vehicle'})


@login_required
@fleet_manager_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.registration_number} updated successfully.")
            return redirect('fleet:vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'fleet/vehicle_form.html', {'form': form, 'vehicle': vehicle, 'title': f'Edit Vehicle: {vehicle.registration_number}'})


@login_required
@admin_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    # Check if active in ongoing routes
    if vehicle.routes.filter(status__in=['Scheduled', 'In Transit']).exists():
        messages.error(request, f"Cannot delete vehicle {vehicle.registration_number} because it is assigned to an active route.")
        return redirect('fleet:vehicle_detail', pk=pk)

    if request.method == 'POST':
        reg = vehicle.registration_number
        vehicle.delete()
        messages.success(request, f"Vehicle {reg} has been deleted successfully.")
        return redirect('fleet:vehicle_list')
    return render(request, 'fleet/vehicle_confirm_delete.html', {'vehicle': vehicle})


# Driver Views
@login_required
def driver_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    drivers = Driver.objects.all()

    if search_query:
        drivers = drivers.filter(
            Q(name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(contact_number__icontains=search_query)
        )
    if status_filter:
        drivers = drivers.filter(employment_status=status_filter)

    context = {
        'drivers': drivers,
        'search_query': search_query,
        'status_filter': status_filter,
        'statuses': Driver.STATUS_CHOICES,
    }
    return render(request, 'fleet/driver_list.html', context)


@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    recent_routes = driver.routes.select_related('vehicle').order_by('-departure_datetime')[:8]
    incidents = driver.incidents.select_related('vehicle').order_by('-incident_date')[:5]

    context = {
        'driver': driver,
        'recent_routes': recent_routes,
        'incidents': incidents,
    }
    return render(request, 'fleet/driver_detail.html', context)


@login_required
@fleet_manager_required
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save()
            messages.success(request, f"Driver {driver.name} enrolled successfully.")
            return redirect('fleet:driver_detail', pk=driver.pk)
    else:
        form = DriverForm()
    return render(request, 'fleet/driver_form.html', {'form': form, 'title': 'Enroll New Driver'})


@login_required
@fleet_manager_required
def driver_update(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            driver = form.save()
            messages.success(request, f"Driver {driver.name} updated successfully.")
            return redirect('fleet:driver_detail', pk=driver.pk)
    else:
        form = DriverForm(instance=driver)
    return render(request, 'fleet/driver_form.html', {'form': form, 'driver': driver, 'title': f'Edit Driver: {driver.name}'})


@login_required
@admin_required
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if driver.routes.filter(status__in=['Scheduled', 'In Transit']).exists():
        messages.error(request, f"Cannot delete driver {driver.name} because they are assigned to an active route.")
        return redirect('fleet:driver_detail', pk=pk)

    if request.method == 'POST':
        name = driver.name
        driver.delete()
        messages.success(request, f"Driver {name} removed successfully.")
        return redirect('fleet:driver_list')
    return render(request, 'fleet/driver_confirm_delete.html', {'driver': driver})
