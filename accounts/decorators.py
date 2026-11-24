from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """
    Decorator for views to enforce strict role-based access control.
    allowed_roles: list of role strings, e.g. ['ADMIN', 'FLEET_MANAGER']
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(
                request, 
                "Access Denied: You do not have the required role permissions to perform this action."
            )
            return redirect('accounts:dashboard')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


def fleet_manager_required(view_func):
    return role_required(['ADMIN', 'FLEET_MANAGER'])(view_func)


def maintenance_staff_required(view_func):
    return role_required(['ADMIN', 'MAINTENANCE_STAFF'])(view_func)
