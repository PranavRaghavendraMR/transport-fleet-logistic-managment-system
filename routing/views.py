from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Route
from .forms import RouteForm
from fleet.models import Vehicle, Driver
from accounts.decorators import fleet_manager_required, admin_required


@login_required
def route_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    vehicle_id = request.GET.get('vehicle', '')
    driver_id = request.GET.get('driver', '')

    routes = Route.objects.select_related('vehicle', 'driver').all()

    if search_query:
        routes = routes.filter(
            Q(route_code__icontains=search_query) |
            Q(starting_location__icontains=search_query) |
            Q(destination__icontains=search_query)
        )
    if status_filter:
        routes = routes.filter(status=status_filter)
    if vehicle_id:
        routes = routes.filter(vehicle_id=vehicle_id)
    if driver_id:
        routes = routes.filter(driver_id=driver_id)

    context = {
        'routes': routes,
        'search_query': search_query,
        'status_filter': status_filter,
        'vehicle_id': vehicle_id,
        'driver_id': driver_id,
        'vehicles': Vehicle.objects.all(),
        'drivers': Driver.objects.all(),
        'statuses': Route.STATUS_CHOICES,
    }
    return render(request, 'routing/route_list.html', context)


@login_required
def route_detail(request, pk):
    route = get_object_or_404(Route.objects.select_related('vehicle', 'driver'), pk=pk)
    return render(request, 'routing/route_detail.html', {'route': route})


@login_required
@fleet_manager_required
def route_create(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f"Route {route.route_code} scheduled successfully.")
            return redirect('routing:route_detail', pk=route.pk)
    else:
        form = RouteForm()
    return render(request, 'routing/route_form.html', {'form': form, 'title': 'Create Transportation Route'})


@login_required
@fleet_manager_required
def route_update(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            route = form.save()
            messages.success(request, f"Route {route.route_code} updated successfully.")
            return redirect('routing:route_detail', pk=route.pk)
    else:
        form = RouteForm(instance=route)
    return render(request, 'routing/route_form.html', {'form': form, 'route': route, 'title': f'Edit Route: {route.route_code}'})


@login_required
@fleet_manager_required
def route_status_update(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Route.STATUS_CHOICES):
            route.status = new_status
            if new_status == Route.STATUS_COMPLETED and not route.actual_arrival_datetime:
                route.actual_arrival_datetime = timezone.now()
            route.save()
            messages.success(request, f"Route {route.route_code} status transitioned to {new_status}.")
        else:
            messages.error(request, "Invalid route status specified.")
    return redirect('routing:route_detail', pk=pk)


@login_required
@admin_required
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if route.status == Route.STATUS_IN_TRANSIT:
        messages.error(request, "Cannot delete a route that is currently In Transit.")
        return redirect('routing:route_detail', pk=pk)
        
    if request.method == 'POST':
        code = route.route_code
        route.delete()
        messages.success(request, f"Route {code} has been deleted.")
        return redirect('routing:route_list')
    return render(request, 'routing/route_confirm_delete.html', {'route': route})
