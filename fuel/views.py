from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Q
from decimal import Decimal
import json

from .models import FuelRecord
from .forms import FuelRecordForm
from fleet.models import Vehicle
from accounts.decorators import admin_required


@login_required
def fuel_dashboard(request):
    total_records = FuelRecord.objects.count()
    aggregates = FuelRecord.objects.aggregate(
        total_cost=Sum('total_fuel_cost'),
        total_litres=Sum('fuel_quantity'),
        avg_price=Avg('fuel_price_per_litre'),
    )

    # Average mileage of records with valid calculated mileage
    mileage_records = FuelRecord.objects.filter(calculated_mileage__gt=0)
    avg_fleet_mileage = mileage_records.aggregate(avg=Avg('calculated_mileage'))['avg'] or 0

    # Vehicle-wise fuel analytics
    vehicle_stats = []
    vehicles = Vehicle.objects.prefetch_related('fuel_records').all()
    for v in vehicles:
        v_records = v.fuel_records.all()
        if v_records.exists():
            v_cost = v_records.aggregate(sum=Sum('total_fuel_cost'))['sum'] or 0
            v_litres = v_records.aggregate(sum=Sum('fuel_quantity'))['sum'] or 0
            v_valid_mileage = v_records.filter(calculated_mileage__gt=0).aggregate(avg=Avg('calculated_mileage'))['avg'] or 0
            vehicle_stats.append({
                'vehicle': v,
                'total_cost': v_cost,
                'total_litres': v_litres,
                'avg_mileage': round(v_valid_mileage, 2),
                'refuels_count': v_records.count(),
            })

    # Sort by total cost descending
    vehicle_stats.sort(key=lambda x: x['total_cost'], reverse=True)

    # Recent fuel logs
    recent_records = FuelRecord.objects.select_related('vehicle', 'recorded_by').order_by('-fuel_date')[:8]

    # Chart data for vehicle comparisons
    top_vehicles = vehicle_stats[:6]
    chart_v_labels = [stat['vehicle'].registration_number for stat in top_vehicles]
    chart_v_costs = [float(stat['total_cost']) for stat in top_vehicles]
    chart_v_mileages = [float(stat['avg_mileage']) for stat in top_vehicles]

    context = {
        'total_records': total_records,
        'total_cost': aggregates['total_cost'] or 0,
        'total_litres': aggregates['total_litres'] or 0,
        'avg_price': round(aggregates['avg_price'] or 0, 2),
        'avg_fleet_mileage': round(avg_fleet_mileage, 2),
        'vehicle_stats': vehicle_stats,
        'recent_records': recent_records,
        'chart_v_labels': json.dumps(chart_v_labels),
        'chart_v_costs': json.dumps(chart_v_costs),
        'chart_v_mileages': json.dumps(chart_v_mileages),
    }
    return render(request, 'fuel/fuel_dashboard.html', context)


@login_required
def fuel_list(request):
    search_query = request.GET.get('q', '').strip()
    vehicle_id = request.GET.get('vehicle', '')
    fuel_type = request.GET.get('fuel_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    records = FuelRecord.objects.select_related('vehicle', 'recorded_by').all()

    if search_query:
        records = records.filter(
            Q(fuel_station__icontains=search_query) |
            Q(invoice_number__icontains=search_query) |
            Q(vehicle__registration_number__icontains=search_query)
        )
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)
    if fuel_type:
        records = records.filter(fuel_type=fuel_type)
    if start_date:
        records = records.filter(fuel_date__gte=start_date)
    if end_date:
        records = records.filter(fuel_date__lte=end_date)

    context = {
        'records': records,
        'search_query': search_query,
        'vehicle_id': vehicle_id,
        'fuel_type': fuel_type,
        'start_date': start_date,
        'end_date': end_date,
        'vehicles': Vehicle.objects.all(),
        'fuel_types': FuelRecord.FUEL_TYPE_CHOICES,
    }
    return render(request, 'fuel/fuel_list.html', context)


@login_required
def fuel_detail(request, pk):
    record = get_object_or_404(FuelRecord.objects.select_related('vehicle', 'recorded_by'), pk=pk)
    # Find previous record for context
    prev_record = FuelRecord.objects.filter(
        vehicle=record.vehicle, 
        odometer_reading__lt=record.odometer_reading
    ).order_by('-odometer_reading').first()

    return render(request, 'fuel/fuel_detail.html', {
        'record': record,
        'prev_record': prev_record,
    })


@login_required
def fuel_create(request):
    vehicle_id = request.GET.get('vehicle_id')
    initial = {}
    if vehicle_id:
        initial['vehicle'] = vehicle_id

    if request.method == 'POST':
        form = FuelRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, f"Fuel purchase for {record.vehicle.registration_number} saved. Total: ₹{record.total_fuel_cost}")
            return redirect('fuel:fuel_detail', pk=record.pk)
    else:
        form = FuelRecordForm(initial=initial)
    return render(request, 'fuel/fuel_form.html', {'form': form, 'title': 'Log Fuel Purchase'})


@login_required
def fuel_update(request, pk):
    record = get_object_or_404(FuelRecord, pk=pk)
    if request.method == 'POST':
        form = FuelRecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"Fuel entry for {record.vehicle.registration_number} updated.")
            return redirect('fuel:fuel_detail', pk=record.pk)
    else:
        form = FuelRecordForm(instance=record)
    return render(request, 'fuel/fuel_form.html', {'form': form, 'record': record, 'title': f'Edit Fuel Log: {record.vehicle.registration_number}'})


@login_required
@admin_required
def fuel_delete(request, pk):
    record = get_object_or_404(FuelRecord, pk=pk)
    if request.method == 'POST':
        reg = record.vehicle.registration_number
        record.delete()
        messages.success(request, f"Fuel record for {reg} removed.")
        return redirect('fuel:fuel_list')
    return render(request, 'fuel/fuel_confirm_delete.html', {'record': record})
