from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_FLEET_MANAGER = 'FLEET_MANAGER'
    ROLE_MAINTENANCE_STAFF = 'MAINTENANCE_STAFF'
    ROLE_GENERAL_STAFF = 'GENERAL_STAFF'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_FLEET_MANAGER, 'Fleet Manager'),
        (ROLE_MAINTENANCE_STAFF, 'Maintenance Staff'),
        (ROLE_GENERAL_STAFF, 'General Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default=ROLE_GENERAL_STAFF)
    employee_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, default='Transport & Fleet Operations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    @property
    def is_fleet_manager(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_FLEET_MANAGER] or self.user.is_superuser

    @property
    def is_maintenance_staff(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_MAINTENANCE_STAFF] or self.user.is_superuser

    @property
    def is_general_staff(self):
        return True


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_GENERAL_STAFF
        UserProfile.objects.create(user=instance, role=role, employee_id=f"EMP{instance.id:04d}")
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
