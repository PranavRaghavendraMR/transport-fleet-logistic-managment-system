from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from .models import SafetyIncident, SafetyInspection
from .forms import SafetyIncidentForm, SafetyInspectionForm
from fleet.models import Vehicle, Driver
from accounts.decorators import admin_required


@login_required
def safety_dashboard(request):
    today = date.today()
    thirty_days = today + timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)

    total_incidents = SafetyIncident.objects.count()
    open_incidents = SafetyIncident.objects.filter(
        status__in=[SafetyIncident.STATUS_REPORTED, SafetyIncident.STATUS_INVESTIGATING]
    ).count()
    resolved_incidents = SafetyIncident.objects.filter(
        status__in=[SafetyIncident.STATUS_RESOLVED, SafetyIncident.STATUS_CLOSED]
    ).count()

    total_damage_cost = SafetyIncident.objects.aggregate(total=Sum('estimated_damage_cost'))['total'] or 0

    # Inspection stats
    total_inspections = SafetyInspection.objects.count()
    failed_inspections = SafetyInspection.objects.filter(
        overall_inspection_result=SafetyInspection.RESULT_FAILED
    ).count()

    # Vehicles needing inspection: vehicles with no inspection in past 90 days or last inspection failed
    vehicles_needing_inspection = []
    for v in Vehicle.objects.all():
        latest_insp = v.inspections.order_by('-inspection_date').first()
        if not latest_insp or latest_insp.inspection_date < ninety_days_ago or latest_insp.overall_inspection_result == SafetyInspection.RESULT_FAILED:
            vehicles_needing_inspection.append({
                'vehicle': v,
                'last_inspection': latest_insp.inspection_date if latest_insp else 'Never',
                'result': latest_insp.overall_inspection_result if latest_insp else 'No Record',
            })

    # Expired or expiring documents
    expiring_insurance = Vehicle.objects.filter(insurance_expiry_date__lte=thirty_days).order_by('insurance_expiry_date')
    expiring_licenses = Driver.objects.filter(license_expiry_date__lte=thirty_days).order_by('license_expiry_date')

    # Breakdown by severity
    severity_breakdown = SafetyIncident.objects.values('damage_severity').annotate(
        count=Count('id'),
        cost=Sum('estimated_damage_cost')
    ).order_by('damage_severity')

    # Recent items
    recent_incidents = SafetyIncident.objects.select_related('vehicle', 'driver').order_by('-incident_date')[:6]
    recent_inspections = SafetyInspection.objects.select_related('vehicle').order_by('-inspection_date')[:6]

    context = {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
        'total_damage_cost': total_damage_cost,
        'total_inspections': total_inspections,
        'failed_inspections': failed_inspections,
        'vehicles_needing_inspection': vehicles_needing_inspection,
        'expiring_insurance': expiring_insurance,
        'expiring_licenses': expiring_licenses,
        'severity_breakdown': severity_breakdown,
        'recent_incidents': recent_incidents,
        'recent_inspections': recent_inspections,
    }
    return render(request, 'safety/safety_dashboard.html', context)


# Incident Views
@login_required
def incident_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    severity_filter = request.GET.get('severity', '')
    vehicle_id = request.GET.get('vehicle', '')

    incidents = SafetyIncident.objects.select_related('vehicle', 'driver').all()

    if search_query:
        incidents = incidents.filter(
            Q(incident_id__icontains=search_query) |
            Q(incident_location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vehicle__registration_number__icontains=search_query)
        )
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if severity_filter:
        incidents = incidents.filter(damage_severity=severity_filter)
    if vehicle_id:
        incidents = incidents.filter(vehicle_id=vehicle_id)

    context = {
        'incidents': incidents,
        'search_query': search_query,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'vehicle_id': vehicle_id,
        'vehicles': Vehicle.objects.all(),
        'statuses': SafetyIncident.STATUS_CHOICES,
        'severities': SafetyIncident.SEVERITY_CHOICES,
    }
    return render(request, 'safety/incident_list.html', context)


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(SafetyIncident.objects.select_related('vehicle', 'driver'), pk=pk)
    return render(request, 'safety/incident_detail.html', {'incident': incident})


@login_required
def incident_create(request):
    if request.method == 'POST':
        form = SafetyIncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            messages.success(request, f"Incident {incident.incident_id} filed successfully.")
            return redirect('safety:incident_detail', pk=incident.pk)
    else:
        # Generate initial incident ID
        next_num = SafetyIncident.objects.count() + 1
        initial_id = f"INC-2026-{next_num:03d}"
        form = SafetyIncidentForm(initial={'incident_id': initial_id, 'incident_date': date.today()})
    return render(request, 'safety/incident_form.html', {'form': form, 'title': 'Report Safety Incident'})


@login_required
def incident_update(request, pk):
    incident = get_object_or_404(SafetyIncident, pk=pk)
    if request.method == 'POST':
        form = SafetyIncidentForm(request.POST, instance=incident)
        if form.is_valid():
            incident = form.save()
            messages.success(request, f"Incident {incident.incident_id} updated successfully.")
            return redirect('safety:incident_detail', pk=incident.pk)
    else:
        form = SafetyIncidentForm(instance=incident)
    return render(request, 'safety/incident_form.html', {'form': form, 'incident': incident, 'title': f'Edit Incident: {incident.incident_id}'})


@login_required
@admin_required
def incident_delete(request, pk):
    incident = get_object_or_404(SafetyIncident, pk=pk)
    if request.method == 'POST':
        inc_id = incident.incident_id
        incident.delete()
        messages.success(request, f"Incident {inc_id} removed.")
        return redirect('safety:incident_list')
    return render(request, 'safety/incident_confirm_delete.html', {'incident': incident})


# Inspection Views
@login_required
def inspection_list(request):
    inspections = SafetyInspection.objects.select_related('vehicle').all()
    result_filter = request.GET.get('result', '')
    vehicle_id = request.GET.get('vehicle', '')

    if result_filter:
        inspections = inspections.filter(overall_inspection_result=result_filter)
    if vehicle_id:
        inspections = inspections.filter(vehicle_id=vehicle_id)

    context = {
        'inspections': inspections,
        'result_filter': result_filter,
        'vehicle_id': vehicle_id,
        'vehicles': Vehicle.objects.all(),
        'results': SafetyInspection.RESULT_CHOICES,
    }
    return render(request, 'safety/inspection_list.html', context)


@login_required
def inspection_detail(request, pk):
    inspection = get_object_or_404(SafetyInspection.objects.select_related('vehicle'), pk=pk)
    return render(request, 'safety/inspection_detail.html', {'inspection': inspection})


@login_required
def inspection_create(request):
    if request.method == 'POST':
        form = SafetyInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save()
            messages.success(request, f"Safety inspection {inspection.inspection_id} recorded successfully.")
            return redirect('safety:inspection_detail', pk=inspection.pk)
    else:
        next_num = SafetyInspection.objects.count() + 1
        initial_id = f"INSP-2026-{next_num:03d}"
        form = SafetyInspectionForm(initial={'inspection_id': initial_id, 'inspection_date': date.today(), 'inspector_name': request.user.get_full_name() or request.user.username})
    return render(request, 'safety/inspection_form.html', {'form': form, 'title': 'Perform Safety Inspection'})
