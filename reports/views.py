from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Q
from datetime import date
from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident, SafetyInspection
from fuel.models import FuelRecord


@login_required
def reports_home(request):
    return render(request, 'reports/reports_home.html')


@login_required
def vehicle_inventory_report(request):
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    fuel_filter = request.GET.get('fuel', '')

    vehicles = Vehicle.objects.all()
    if type_filter:
        vehicles = vehicles.filter(vehicle_type=type_filter)
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if fuel_filter:
        vehicles = vehicles.filter(fuel_type=fuel_filter)

    total_capacity = vehicles.aggregate(total=Sum('capacity_kg'))['total'] or 0

    context = {
        'vehicles': vehicles,
        'total_capacity': total_capacity,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'fuel_filter': fuel_filter,
        'types': Vehicle.VEHICLE_TYPE_CHOICES,
        'statuses': Vehicle.STATUS_CHOICES,
        'fuel_types': Vehicle.FUEL_TYPE_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/vehicle_inventory_report.html', context)


@login_required
def vehicle_availability_report(request):
    available_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_AVAILABLE)
    in_use_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_IN_USE)
    maintenance_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_MAINTENANCE)

    context = {
        'available_vehicles': available_vehicles,
        'in_use_vehicles': in_use_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'total_count': Vehicle.objects.count(),
        'available_count': available_vehicles.count(),
        'in_use_count': in_use_vehicles.count(),
        'maintenance_count': maintenance_vehicles.count(),
        'report_date': date.today(),
    }
    return render(request, 'reports/vehicle_availability_report.html', context)


@login_required
def driver_report(request):
    status_filter = request.GET.get('status', '')
    drivers = Driver.objects.all()
    if status_filter:
        drivers = drivers.filter(employment_status=status_filter)

    context = {
        'drivers': drivers,
        'status_filter': status_filter,
        'statuses': Driver.STATUS_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/driver_report.html', context)


@login_required
def route_performance_report(request):
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    vehicle_id = request.GET.get('vehicle', '')

    routes = Route.objects.select_related('vehicle', 'driver').all()
    if status_filter:
        routes = routes.filter(status=status_filter)
    if start_date:
        routes = routes.filter(departure_datetime__date__gte=start_date)
    if end_date:
        routes = routes.filter(departure_datetime__date__lte=end_date)
    if vehicle_id:
        routes = routes.filter(vehicle_id=vehicle_id)

    total_distance = routes.aggregate(sum=Sum('distance_km'))['sum'] or 0

    context = {
        'routes': routes,
        'total_distance': total_distance,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'vehicle_id': vehicle_id,
        'vehicles': Vehicle.objects.all(),
        'statuses': Route.STATUS_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/route_performance_report.html', context)


@login_required
def maintenance_history_report(request):
    vehicle_id = request.GET.get('vehicle', '')
    type_filter = request.GET.get('type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    records = MaintenanceRecord.objects.select_related('vehicle').all()
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)
    if type_filter:
        records = records.filter(maintenance_type=type_filter)
    if start_date:
        records = records.filter(service_date__gte=start_date)
    if end_date:
        records = records.filter(service_date__lte=end_date)

    totals = records.aggregate(
        total=Sum('total_cost'),
        spare=Sum('spare_parts_cost'),
        labour=Sum('labour_cost')
    )

    context = {
        'records': records,
        'total_cost': totals['total'] or 0,
        'total_spare': totals['spare'] or 0,
        'total_labour': totals['labour'] or 0,
        'vehicle_id': vehicle_id,
        'type_filter': type_filter,
        'start_date': start_date,
        'end_date': end_date,
        'vehicles': Vehicle.objects.all(),
        'types': MaintenanceRecord.MAINTENANCE_TYPE_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/maintenance_history_report.html', context)


@login_required
def maintenance_expense_report(request):
    # Aggregated maintenance expenses by vehicle
    vehicles = Vehicle.objects.all()
    vehicle_expenses = []
    for v in vehicles:
        m_agg = v.maintenance_records.aggregate(
            total=Sum('total_cost'),
            spare=Sum('spare_parts_cost'),
            labour=Sum('labour_cost'),
            count=Count('id')
        )
        if m_agg['count'] > 0:
            vehicle_expenses.append({
                'vehicle': v,
                'count': m_agg['count'],
                'spare': m_agg['spare'] or 0,
                'labour': m_agg['labour'] or 0,
                'total': m_agg['total'] or 0,
            })

    vehicle_expenses.sort(key=lambda x: x['total'], reverse=True)
    grand_total = sum(x['total'] for x in vehicle_expenses)

    context = {
        'vehicle_expenses': vehicle_expenses,
        'grand_total': grand_total,
        'report_date': date.today(),
    }
    return render(request, 'reports/maintenance_expense_report.html', context)


@login_required
def safety_incident_report(request):
    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', '')
    vehicle_id = request.GET.get('vehicle', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    incidents = SafetyIncident.objects.select_related('vehicle', 'driver').all()
    if severity_filter:
        incidents = incidents.filter(damage_severity=severity_filter)
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if vehicle_id:
        incidents = incidents.filter(vehicle_id=vehicle_id)
    if start_date:
        incidents = incidents.filter(incident_date__gte=start_date)
    if end_date:
        incidents = incidents.filter(incident_date__lte=end_date)

    total_damage = incidents.aggregate(sum=Sum('estimated_damage_cost'))['sum'] or 0

    context = {
        'incidents': incidents,
        'total_damage': total_damage,
        'severity_filter': severity_filter,
        'status_filter': status_filter,
        'vehicle_id': vehicle_id,
        'start_date': start_date,
        'end_date': end_date,
        'vehicles': Vehicle.objects.all(),
        'severities': SafetyIncident.SEVERITY_CHOICES,
        'statuses': SafetyIncident.STATUS_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/safety_incident_report.html', context)


@login_required
def fuel_expense_report(request):
    vehicle_id = request.GET.get('vehicle', '')
    fuel_type = request.GET.get('fuel_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    records = FuelRecord.objects.select_related('vehicle').all()
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)
    if fuel_type:
        records = records.filter(fuel_type=fuel_type)
    if start_date:
        records = records.filter(fuel_date__gte=start_date)
    if end_date:
        records = records.filter(fuel_date__lte=end_date)

    totals = records.aggregate(
        total_cost=Sum('total_fuel_cost'),
        total_litres=Sum('fuel_quantity'),
        avg_price=Avg('fuel_price_per_litre')
    )

    context = {
        'records': records,
        'total_cost': totals['total_cost'] or 0,
        'total_litres': totals['total_litres'] or 0,
        'avg_price': round(totals['avg_price'] or 0, 2),
        'vehicle_id': vehicle_id,
        'fuel_type': fuel_type,
        'start_date': start_date,
        'end_date': end_date,
        'vehicles': Vehicle.objects.all(),
        'fuel_types': FuelRecord.FUEL_TYPE_CHOICES,
        'report_date': date.today(),
    }
    return render(request, 'reports/fuel_expense_report.html', context)


@login_required
def vehicle_mileage_report(request):
    # Fleet mileage analysis
    vehicles = Vehicle.objects.all()
    vehicle_mileages = []
    for v in vehicles:
        valid_records = v.fuel_records.filter(calculated_mileage__gt=0)
        total_fuel = v.fuel_records.aggregate(sum=Sum('fuel_quantity'))['sum'] or 0
        total_cost = v.fuel_records.aggregate(sum=Sum('total_fuel_cost'))['sum'] or 0
        
        if valid_records.exists():
            avg_mileage = valid_records.aggregate(avg=Avg('calculated_mileage'))['avg'] or 0
            best_mileage = valid_records.order_by('-calculated_mileage').first().calculated_mileage
            worst_mileage = valid_records.order_by('calculated_mileage').first().calculated_mileage
        else:
            avg_mileage = 0
            best_mileage = 0
            worst_mileage = 0

        vehicle_mileages.append({
            'vehicle': v,
            'avg_mileage': round(avg_mileage, 2),
            'best_mileage': best_mileage,
            'worst_mileage': worst_mileage,
            'total_fuel': total_fuel,
            'total_cost': total_cost,
            'odometer': v.current_odometer,
        })

    vehicle_mileages.sort(key=lambda x: x['avg_mileage'], reverse=True)

    context = {
        'vehicle_mileages': vehicle_mileages,
        'report_date': date.today(),
    }
    return render(request, 'reports/vehicle_mileage_report.html', context)
