def user_role_context(request):
    """
    Context processor to easily check permissions and roles in any template.
    """
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        role = profile.role if profile else ('ADMIN' if request.user.is_superuser else 'GENERAL_STAFF')
        return {
            'user_profile': profile,
            'current_role': role,
            'is_admin': request.user.is_superuser or (profile and profile.is_admin),
            'is_fleet_manager': request.user.is_superuser or (profile and profile.is_fleet_manager),
            'is_maintenance_staff': request.user.is_superuser or (profile and profile.is_maintenance_staff),
            'is_general_staff': True,
        }
    return {
        'user_profile': None,
        'current_role': None,
        'is_admin': False,
        'is_fleet_manager': False,
        'is_maintenance_staff': False,
        'is_general_staff': False,
    }
