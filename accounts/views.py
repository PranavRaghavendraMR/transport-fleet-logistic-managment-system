from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

from accounts.models import UserProfile
from accounts.decorators import admin_required
from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident, SafetyInspection
from fuel.models import FuelRecord


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Your account has been deactivated. Please contact the administrator.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out of the Fleet Management System.")
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    # Core KPI statistics
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_AVAILABLE).count()
    in_use_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_IN_USE).count()
    maintenance_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_MAINTENANCE).count()
    
    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(employment_status=Driver.STATUS_ACTIVE).count()
    
    active_routes = Route.objects.filter(status__in=[Route.STATUS_SCHEDULED, Route.STATUS_IN_TRANSIT]).count()
    in_transit_routes = Route.objects.filter(status=Route.STATUS_IN_TRANSIT).count()
    
    pending_maintenance = MaintenanceRecord.objects.filter(
        status__in=[MaintenanceRecord.STATUS_SCHEDULED, MaintenanceRecord.STATUS_IN_PROGRESS]
    ).count()
    
    total_fuel_cost = FuelRecord.objects.aggregate(total=Sum('total_fuel_cost'))['total'] or 0
    total_maintenance_cost = MaintenanceRecord.objects.aggregate(total=Sum('total_cost'))['total'] or 0
    
    open_incidents_count = SafetyIncident.objects.filter(
        status__in=[SafetyIncident.STATUS_REPORTED, SafetyIncident.STATUS_INVESTIGATING]
    ).count()

    # Expiring documents checks (within 30 days)
    today = date.today()
    thirty_days = today + timedelta(days=30)
    
    expiring_insurance = Vehicle.objects.filter(insurance_expiry_date__lte=thirty_days)
    expiring_licenses = Driver.objects.filter(license_expiry_date__lte=thirty_days)
    
    # Recent items
    recent_routes = Route.objects.select_related('vehicle', 'driver').order_by('-departure_datetime')[:6]
    upcoming_maintenance = MaintenanceRecord.objects.select_related('vehicle').filter(
        status__in=[MaintenanceRecord.STATUS_SCHEDULED, MaintenanceRecord.STATUS_IN_PROGRESS]
    ).order_by('service_date')[:5]
    recent_incidents = SafetyIncident.objects.select_related('vehicle', 'driver').order_by('-incident_date')[:5]
    
    # Monthly charts data generation (past 6 months)
    months_labels = []
    monthly_fuel_data = []
    monthly_maint_data = []

    for i in range(5, -1, -1):
        target_month_date = today.replace(day=1) - timedelta(days=i*30)
        m_label = target_month_date.strftime("%b %Y")
        months_labels.append(m_label)
        
        m_start = target_month_date.replace(day=1)
        # Approximate end of month
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year+1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month+1, day=1)
            
        f_cost = FuelRecord.objects.filter(
            fuel_date__gte=m_start, 
            fuel_date__lt=m_end
        ).aggregate(sum=Sum('total_fuel_cost'))['sum'] or 0
        monthly_fuel_data.append(float(f_cost))
        
        m_cost = MaintenanceRecord.objects.filter(
            service_date__gte=m_start, 
            service_date__lt=m_end
        ).aggregate(sum=Sum('total_cost'))['sum'] or 0
        monthly_maint_data.append(float(m_cost))

    # Vehicle type breakdown
    vehicle_types = list(Vehicle.objects.values('vehicle_type').annotate(count=Count('id')).order_by('vehicle_type'))
    vtype_labels = [item['vehicle_type'] for item in vehicle_types]
    vtype_counts = [item['count'] for item in vehicle_types]

    context = {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'in_use_vehicles': in_use_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'total_drivers': total_drivers,
        'active_drivers': active_drivers,
        'active_routes': active_routes,
        'in_transit_routes': in_transit_routes,
        'pending_maintenance': pending_maintenance,
        'total_fuel_cost': total_fuel_cost,
        'total_maintenance_cost': total_maintenance_cost,
        'open_incidents_count': open_incidents_count,
        'expiring_insurance': expiring_insurance,
        'expiring_licenses': expiring_licenses,
        'recent_routes': recent_routes,
        'upcoming_maintenance': upcoming_maintenance,
        'recent_incidents': recent_incidents,
        # Chart JSON
        'chart_status_data': json.dumps([available_vehicles, in_use_vehicles, maintenance_vehicles]),
        'chart_months': json.dumps(months_labels),
        'chart_fuel_data': json.dumps(monthly_fuel_data),
        'chart_maint_data': json.dumps(monthly_maint_data),
        'chart_vtype_labels': json.dumps(vtype_labels),
        'chart_vtype_counts': json.dumps(vtype_counts),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        department = request.POST.get('department', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        if profile:
            profile.phone = phone
            profile.department = department
            profile.save()

        messages.success(request, "Your profile details have been updated successfully.")
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
@admin_required
def users_list_view(request):
    users = User.objects.select_related('profile').all().order_by('username')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, id=user_id)

        if action == 'change_role':
            new_role = request.POST.get('role')
            if hasattr(target_user, 'profile'):
                target_user.profile.role = new_role
                target_user.profile.save()
                messages.success(request, f"Role updated for {target_user.username} to {new_role}.")
        elif action == 'toggle_status':
            if target_user == request.user:
                messages.error(request, "You cannot deactivate your own administrative account.")
            else:
                target_user.is_active = not target_user.is_active
                target_user.save()
                status_str = "activated" if target_user.is_active else "deactivated"
                messages.info(request, f"Account {target_user.username} {status_str}.")
        return redirect('accounts:users_list')

    return render(request, 'accounts/users_list.html', {
        'users': users, 
        'role_choices': UserProfile.ROLE_CHOICES
    })
