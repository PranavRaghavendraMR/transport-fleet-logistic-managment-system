from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date
from .models import MaintenanceRecord
from .forms import MaintenanceRecordForm
from fleet.models import Vehicle
from accounts.decorators import maintenance_staff_required, admin_required


@login_required
def maintenance_dashboard(request):
    today = date.today()
    total_records = MaintenanceRecord.objects.count()
    scheduled_count = MaintenanceRecord.objects.filter(status=MaintenanceRecord.STATUS_SCHEDULED).count()
    in_progress_count = MaintenanceRecord.objects.filter(status=MaintenanceRecord.STATUS_IN_PROGRESS).count()
    completed_count = MaintenanceRecord.objects.filter(status=MaintenanceRecord.STATUS_COMPLETED).count()
    
    total_cost_agg = MaintenanceRecord.objects.aggregate(
        total=Sum('total_cost'),
        spare=Sum('spare_parts_cost'),
        labour=Sum('labour_cost')
    )
    
    overdue_records = MaintenanceRecord.objects.filter(
        status__in=[MaintenanceRecord.STATUS_SCHEDULED, MaintenanceRecord.STATUS_IN_PROGRESS],
        service_date__lt=today
    ).select_related('vehicle')
    
    upcoming_records = MaintenanceRecord.objects.filter(
        status=MaintenanceRecord.STATUS_SCHEDULED,
        service_date__gte=today
    ).select_related('vehicle').order_by('service_date')[:6]
    
    recent_completed = MaintenanceRecord.objects.filter(
        status=MaintenanceRecord.STATUS_COMPLETED
    ).select_related('vehicle').order_by('-service_date')[:6]

    # Aggregation by type
    type_breakdown = MaintenanceRecord.objects.values('maintenance_type').annotate(
        total_cost=Sum('total_cost'),
        count=Count('id')
    ).order_by('-total_cost')

    context = {
        'total_records': total_records,
        'scheduled_count': scheduled_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'total_cost': total_cost_agg['total'] or 0,
        'total_spare_cost': total_cost_agg['spare'] or 0,
        'total_labour_cost': total_cost_agg['labour'] or 0,
        'overdue_records': overdue_records,
        'upcoming_records': upcoming_records,
        'recent_completed': recent_completed,
        'type_breakdown': type_breakdown,
    }
    return render(request, 'maintenance/maintenance_dashboard.html', context)


@login_required
def maintenance_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    vehicle_id = request.GET.get('vehicle', '')

    records = MaintenanceRecord.objects.select_related('vehicle').all()

    if search_query:
        records = records.filter(
            Q(workshop_name__icontains=search_query) |
            Q(technician_name__icontains=search_query) |
            Q(description_of_issue__icontains=search_query) |
            Q(vehicle__registration_number__icontains=search_query)
        )
    if status_filter:
        records = records.filter(status=status_filter)
    if type_filter:
        records = records.filter(maintenance_type=type_filter)
    if vehicle_id:
        records = records.filter(vehicle_id=vehicle_id)

    context = {
        'records': records,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'vehicle_id': vehicle_id,
        'vehicles': Vehicle.objects.all(),
        'types': MaintenanceRecord.MAINTENANCE_TYPE_CHOICES,
        'statuses': MaintenanceRecord.STATUS_CHOICES,
    }
    return render(request, 'maintenance/maintenance_list.html', context)


@login_required
def maintenance_detail(request, pk):
    record = get_object_or_404(MaintenanceRecord.objects.select_related('vehicle'), pk=pk)
    return render(request, 'maintenance/maintenance_detail.html', {'record': record})


@login_required
@maintenance_staff_required
def maintenance_create(request):
    vehicle_id = request.GET.get('vehicle_id')
    initial = {}
    if vehicle_id:
        initial['vehicle'] = vehicle_id

    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"Maintenance record for {record.vehicle.registration_number} logged successfully.")
            return redirect('maintenance:maintenance_detail', pk=record.pk)
    else:
        form = MaintenanceRecordForm(initial=initial)
    return render(request, 'maintenance/maintenance_form.html', {'form': form, 'title': 'Log / Schedule Maintenance'})


@login_required
@maintenance_staff_required
def maintenance_update(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"Maintenance record updated for {record.vehicle.registration_number}.")
            return redirect('maintenance:maintenance_detail', pk=record.pk)
    else:
        form = MaintenanceRecordForm(instance=record)
    return render(request, 'maintenance/maintenance_form.html', {'form': form, 'record': record, 'title': f'Edit Maintenance Record: {record.vehicle.registration_number}'})


@login_required
@maintenance_staff_required
def maintenance_quick_status(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('completion_notes', '').strip()
        if new_status in dict(MaintenanceRecord.STATUS_CHOICES):
            record.status = new_status
            if notes:
                record.work_completion_notes = notes
            record.save()
            messages.success(request, f"Maintenance status transitioned to {new_status} for {record.vehicle.registration_number}.")
        else:
            messages.error(request, "Invalid maintenance status.")
    return redirect('maintenance:maintenance_detail', pk=pk)


@login_required
@admin_required
def maintenance_delete(request, pk):
    record = get_object_or_404(MaintenanceRecord, pk=pk)
    if request.method == 'POST':
        reg = record.vehicle.registration_number
        record.delete()
        messages.success(request, f"Maintenance entry for {reg} has been removed.")
        return redirect('maintenance:maintenance_list')
    return render(request, 'maintenance/maintenance_confirm_delete.html', {'record': record})
